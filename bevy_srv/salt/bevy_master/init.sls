# state file to configure salt-cloud along with salt-master
#
# NOTE:  this state is intended to be run using "sudo salt-call ..." on the machine which will be the master
#
# ANOTHER NOTE: edit the vbox_settings.sls pillar definition when the version of VirtualBox changes
#
{% set my_username = salt['config.get']('my_linux_user') %}
{% set other_minion = "2" if salt['config.get']('run_second_minion') else "" %}

bevy_master_grain:
  grains.list_present:
    - name: roles
    - value:
      - bevy_master
update_the_grains:
  module.run:
    - name: saltutil.sync_grains

include:
  - sdb
  - ./populate_bootstrap_settings
  - configure_bevy_member  {# master is a member, too #}

{% if salt['file.directory_exists']('/vagrant/bevy_srv/salt/pki_cache') %}
restore_keys_from_cache:
  file.recurse:
    - source: salt://pki_cache
    - clean: false
    - name: /etc/salt
{% else %}  {# must make new keys #}
generate-own-key:
  cmd.run:  # generates a minion key, if it does not already exist
    - name: salt-key --gen-keys=minion --auto-create --gen-keys-dir=/etc/salt/pki/minion{{ other_minion }}
    - creates:
      - /etc/salt/pki/minion{{ other_minion }}/minion.pem
      - /etc/salt/pki/minion{{ other_minion }}/minion.pub
    - require:
      - pkg: salt-master
    - require_in:
      - accept-own-key

accept-own-key:
  file.copy:
    - name: /etc/salt/pki/master/minions/bevymaster
    - source: "/etc/salt/pki/minion{{ other_minion }}/minion.pub"   # accept yourself as a minion
    - makedirs: true
    - require:
      - cmd: wait_until_end

clean_up_own_pki:
  file.absent:  # clean up
    - names:
      - /etc/salt/pki/master/minions_pre/bevymaster
      - /etc/salt/pki/master/minions_autosign/bevymaster
    - onlyif:
      - test -e /etc/salt/pki/master/minions/bevymaster
    - require:
      - accept-own-key
{% endif %}

pip2-installed:  # TODO: what about pip3?
  pkg.installed:
    - name: python-pip

salt-master:
  pkg.installed:
    - unless:  # see if salt-master is already installed
      - 'salt-run --version'

salt-cloud:
  pkg.installed:
    - unless:  # see if cloud-master is already installed
      - 'salt-cloud --version'


salt-master-config:
  file.managed:
    - name: /etc/salt/master.d/01_master_from_bootstrap.conf
    - source: salt://bevy_master/files/01_from_bootstrap.conf.jinja
    - template: jinja
    - makedirs: true

#/etc/salt/pki/master/minions/mydns.pub:    # pre-accept the nameserver minion
#  file.managed:
#    - mode: 644
#    - source: salt://bevy_master/mydns.pub
#    - makedirs: true

/etc/salt:
  file.directory:  {# allow the user to easily edit configuration files #}
    - user: {{ my_username }}
    - makedirs: true
    - group: staff
    - mode: 775
    - recurse:
      - user
      - group
      - mode
    - require:
      - wait_until_end

/srv/salt/README.txt:
  file.managed:
    - user: {{ my_username }}
    - group: staff
    - makedirs: true
    - mode: 664
    - source: salt://bevy_master/files/README.notice.jinja
    - template: jinja

/srv/pillar/README.txt:
  file.managed:
    - user: {{ my_username }}
    - group: staff
    - makedirs: true
    - mode: 664
    - source: salt://bevy_master/files/README.notice.jinja
    - template: jinja

/srv/salt/top.sls:
  file.managed:  # make the initial copy of top.sls
    - user: {{ my_username }}
    - group: staff
    - makedirs: true
    - mode: 664
    - source: salt://bevy_master/files/top.sls.jinja
    - template: jinja
    - replace: false

/etc/salt/cloud.conf.d/01_cloud_from_bootstrap.conf:
  file.managed:
    - source: salt://bevy_master/files/cloud.conf
    - makedirs: true
    - user: {{ my_username }}
    - group: staff
    - template: jinja

/etc/salt/cloud.providers:
  file.managed:
    - contents: |
        # managed by Salt
        #
        # This file is intentionally blank.
        # All significant settings are in the cloud.providers.d directory.

salt_cloud_providers_d:
  file.recurse:
    - name: /etc/salt/cloud.providers.d
    - source: salt://bevy_master/files/cloud.providers.d
    - template: jinja
    - user: {{ my_username }}
    - group: staff

/etc/salt/cloud.profiles:
  file.managed:
    - contents: |
        # managed by Salt
        #
        # This file is intentionally blank.
        # All significant settings are in the cloud.profiles.d directory.


salt_cloud_profiles_d:
  file.recurse:
    - name: /etc/salt/cloud.profiles.d
    - source: salt://bevy_master/files/cloud.profiles.d
    - template: jinja
    - user: {{ my_username }}
    - group: staff

{% if salt['grains.get']('os_family') == 'MacOS' %}
{% set salt_master_service_name = 'com.saltstack.salt.master' %}
# salt-master is a user agent on OS-xkcd.py -- not controlled by SaltStack service.* commands

# !!! N O T E: salt master is not supported on a Mac, but is documented to work

install-mac-master-service:
  file.managed:
    - name: {{ salt['environ.get']('HOME') }}/Library/LaunchAgents/{{ salt_master_service_name }}.plist
    - source: salt://bevy_master/darwin/{{ salt_master_service_name }}.plist
    - makedirs: true
    - template: jinja
    - require:
      - pkg: salt-master

unload-mac-master-service:
  cmd.run:
    - name: launchctl unload {{ salt['environ.get']('HOME') }}/Library/LaunchAgents/{{ salt_master_service_name }}.plist
    - watch:
      - salt-master-config
#      - slap_master_on_cheek
    - require:
      - delay_master_restart
restart-salt-master:   # load-mac-service:
  cmd.run:
    - name: launchctl load {{ salt['environ.get']('HOME') }}/Library/LaunchAgents/{{ salt_master_service_name }}.plist
    - require:
      - unload-mac-master-service  # do this after "last" step

 {% else %}
# salt master is a regular Linux service
restart-salt-master:
  service.running:
    - name: salt-master
    - watch:
      - salt-master-config
#      - slap_master_on_cheek
    - require:
      - delay_master_restart
 {% endif %}

delay_master_restart:
  test.nop:
    - requires:
      - salt_cloud_profiles_d  # not actually required, but used to delay timing of master restart
      - salt_cloud_providers_d # "  "
      - python_modules
      - pkg: salt-master

wait_until_end:
  cmd.run:
    - name: sleep 1
