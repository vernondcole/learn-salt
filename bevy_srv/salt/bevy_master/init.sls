# state file to configure salt-cloud along with salt-master
#
# NOTE:  this state is intended to be run using "sudo salt-call ..." on the machine which will be the master
#
{% set my_username = salt['config.get']('my_linux_user') %}
{% set other_minion = "2" if salt['config.get']('run_second_minion') else "" %}

bevy_master_grain:
  grains.present:
    - name: roles
    - value:  # a list -- to be appended
      - bevy_master

include:
  - sdb

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
    - require:
      - cmd: wait_until_end

wait_until_end:
  cmd.run:
    - name: sleep 1
    - require:
      - restart-salt-master  # which is order: last
clean_up_own_pki:
  file.absent:  # clean up
    - names:
      - /etc/salt/pki/master/minions_pre/bevymaster
      - /etc/salt/pki/master/minions_autosign/bevymaster
    - onlyif:
      - test -e /etc/salt/pki/master/minions/bevymaster
    - require:
      - wait_until_end
      - accept-own-key

{% if salt['grains.get']('os_family') == 'MacOS' %}
make-dirs-visible:
  cmd.run:
    - name: |
        chflags nohidden /opt
        chflags nohidden /etc
        chflags nohidden /var
        chflags nohidden /tmp
{% endif %}

{% if salt['grains.get']('os_family') == 'Debian' and false %} # change flag if you want nfs on bevy master #
install-nfs:
  pkg.installed:
    - name: nfs-kernel-server
nfs-kernel-server:
  service.running:
    - enable: true
  require:
    - pkg: install-nfs
{% endif %}

{% if salt['pillar.get']('vbox_install') %}
# # # TODO: add apt-based install. see  http://www.virtualbox.org/wiki/Linux_Downloads
vagrant-sdk:
  archive:
    - extracted
    - name: /opt/virtualbox/{{ pillar['vbox_version'] }}
    - source: {{ pillar['vbox_sdk_url'] }}
    - skip_verify: true
    - archive_format: zip
    - user: {{ my_username }}
    - group: staff
    - trim_output: 5
    - if_missing: /opt/virtualbox/{{ pillar['vbox_version'] }}/sdk/installer

install-vagrant-sdk:
  cmd.run:
    - name: python vboxapisetup.py install
    - cwd: /opt/virtualbox/{{ pillar['vbox_version'] }}/sdk/installer
    - env:
{% if salt['grains.get']('os_family') == 'MacOS' %}
      - VBOX_INSTALL_PATH: /usr/local/bin/virtualbox
{% elif salt['grains.get']('os_family') == 'Debian' %}
      - VBOX_INSTALL_PATH: /usr/bin/virtualbox
{% endif %}
      - VBOX_VERSION: '{{ pillar['vbox_version'] }}'
    - require:
      - archive: vagrant-sdk
    - unless:
      - python -c "import vboxapi"
{% endif %}

salt-master:
  pkg.installed:
    - unless:  # see if salt-master is already installed
      - 'salt-run --version'

salt-cloud:
  pkg.installed:
    - unless:  # see if cloud-master is already installed
      - 'salt-cloud --version'

{% if salt['grains.get']('os_family') == 'Debian' %}
python-pip:
  pkg.installed:
    - names:
      - python-pip
    - require_in:
      - python-modules
{% endif %}
python_modules:
  pip.installed:
    - names:
      - pyVmomi    # needed to control VMware packages

salt-master-config:
  file.managed:
    - name: /etc/salt/master.d/01_from_bootstrap.conf
    - source: salt://bevy_master/master.conf
    - template: jinja
    - makedirs: true


#/etc/salt/pki/master/minions/mydns.pub:    # pre-accept the nameserver minion
#  file.managed:
#    - mode: 644
#    - source: salt://bevy_master/mydns.pub
#    - makedirs: true

/etc/salt:
  file.directory:
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
    - source: salt://bevy_master/README.notice.jinja
    - template: jinja

/srv/pillar/README.txt:
  file.managed:
    - user: {{ my_username }}
    - group: staff
    - makedirs: true
    - mode: 664
    - source: salt://bevy_master/README.notice.jinja
    - template: jinja

/etc/salt/cloud.conf.d/01_from_bootstrap.conf:
  file.managed:
    - source: salt://bevy_master/cloud.conf
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
    - source: salt://bevy_master/cloud.providers.d
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
    - source: salt://bevy_master/cloud.profiles.d
    - template: jinja
    - user: {{ my_username }}
    - group: staff

{% if salt['grains.get']('os_family') == 'MacOS' %}
{% set salt_master_service_name = 'com.saltstack.salt.master' %}
# salt-master is a user agent on OS-x -- not controlled by SaltStack service.* commands

# !!! N O T E: salt master is not supported on a Mac, but is documented to work

install-mac-service:
  file.managed:
    - name: {{ salt['environ.get']('HOME') }}/Library/LaunchAgents/{{ salt_master_service_name }}.plist
    - source: salt://bevy_master/darwin/{{ salt_master_service_name }}.plist
    - makedirs: true
    - template: jinja
    - require:
      - pkg: salt-master

unload-mac-service:
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
      - unload-mac-service  # do this after "last" step

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

#slap_master_on_cheek:
#  test.succeed_with_changes  # always cause master to reset

delay_master_restart:
  test.nop:
    - requires:
      - salt_cloud_profiles_d  # not actually required, but used to delay timing of master restart
      - salt_cloud_providers_d # "  "
      - python_modules
      - pkg: salt-master

sure_minion_config_file:
  file.managed:
    - name: /etc/salt{{ other_minion }}/minion.d/01_from_bootstrap.conf
    - source: salt://bevy_master/minion_01.conf
    - template: jinja
    - makedirs: true

{% if other_minion == "" %}
# ... using the stock salt-minion instance #
/etc/salt/minion:
  file.managed:
    - contents: |
        #
        # N.O.T.E. : SaltStack management occurs below this level.
        # The actual work is done in the minion.d directory below this.
        #
    - makedirs: true
    - show_changes: false
    - replace: false
{% else %}
# v v v installing a second minion instance to talk with Bevy Master (self) #
/etc/salt{{ other_minion }}/minion:
  file.managed:
    - contents: |
        # {{ pillar['salt_managed_message'] }}
        #
        # This is an empty placeholder file.
        # The actual work is done in the minion.d directory below this.
    - replace: false
    - makedirs: true

make_salt{{ other_minion }}-minion_service:
  file.copy:
    - source: /lib/systemd/system/salt-minion.service
    - name: /lib/systemd/system/salt{{ other_minion }}-minion.service

edit_salt-minion{{ other_minion }}_service:
  file.replace:
    - name: /lib/systemd/system/salt{{ other_minion }}-minion.service
    - pattern: "ExecStart=/usr/bin/salt-minion$"
    - repl: "ExecStart=/usr/bin/salt-minion --config-dir=/etc/salt{{ other_minion }}\n"
    - require:
      - file: make_salt{{ other_minion }}-minion_service

add_salt{{ other_minion }}-call_command:
  file.append:
    - name: /etc/bash.bashrc
    - text:
      - '# v v v v v v  added by Salt  v v v v v v'
      - "alias salt{{ other_minion }}='sudo salt-call --config-dir=/etc/salt{{ other_minion }} \"$@\"'"
      - 'printf ".   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .\\n"'
      - 'printf " * This computer is running a bevy master and a second Salt minion.\\n"'
      - 'printf "\\n"'
      - 'printf " * To use the system Salt master, use the \\\"sudo salt-call\\\" command as usual.\\n"'
      - 'printf "\\n"'
      - 'printf " * For salt-call to the Bevy master, use the \\\"salt{{ other_minion }}\\\" command.  For example:\\n"'
      - 'printf "     salt{{ other_minion }} state.apply saltmine-dump\\n"'
      - 'printf "\\n"'
      - 'printf " * To control the second minion,  use (for example):\\n"'
      - 'printf "     sudo systemctl status salt{{ other_minion }}-minion\\n"'
      - 'printf "\\n"'
      - 'printf " * Normal \\\"sudo salt xxx\\\" commands are for the Bevy Master.\\n"'
      - 'printf ".   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .\\n"'

start-salt{{ other_minion }}-minion:
  service.running:
    - name: salt{{ other_minion }}-minion
    - enable: true
    - require:
      - restart-salt-master
      - file: /etc/salt{{ other_minion }}/minion
    - require_in:
      - wait_until_end

remind_user_to_log_off:
  cmd.run:
    - require:
      - file: restart-the-minion
    - bg: true
    - name: '/tmp/run_command_later.py 15 echo . . . N O T E : System settings have been changed. You should log off and reconnect. . . .'
{% endif %} # endif other_minion

restart-the-minion:
  file.managed:
    - name: /tmp/run_command_later.py
    - source: salt://run_command_later.py
    - mode: 775
    - show_changes: false
restart-the-minion_2:
  cmd.run:
    - bg: true  # do not wait for completion of this command
    - require:
      - file: restart-the-minion
    - order: last
    - shell: /bin/bash
    {% if salt['grains.get']('os_family') == 'MacOS' %}
    - name: "/tmp/run_command_later.py 5 launchctl stop com.saltstack.salt.minion \\; launchctl start com.saltstack.salt.minion"
    {% else %}
    - name: "/tmp/run_command_later.py 5 systemctl restart salt{{ other_minion }}-minion"
    {% endif %}
