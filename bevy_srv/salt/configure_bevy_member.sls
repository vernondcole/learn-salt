---
# salt state file for adding a bevy member station (including master)

include:
  - common
  # - pepper
  # - helper_scripts

# NOTE:  this state is intended to be run using "sudo salt-call ..." on the machine which will be the member
#
# ANOTHER NOTE: edit the vbox_settings.sls pillar definition when the version of VirtualBox changes
#
{% set my_username = salt['config.get']('my_linux_user') %}
{% if salt['config.get']('run_second_minion', false) %}
  {% set other_minion = "2" %}
{% else %}
  {% set other_minion = "" %}
{% endif %}
{% set message = pillar['salt_managed_message'] %}

{% if salt['grains.get']('os_family') == 'MacOS' %}
make-dirs-visible:
  cmd.run:
    - name: |
        chflags nohidden /opt
        chflags nohidden /etc
        chflags nohidden /var
        chflags nohidden /tmp
{% endif %}

{{ salt['config.get']('salt_config_directory') }}{{ other_minion }}/minion.d/vagrant_sdb.conf:
  file.managed:
    - contents: |
        {{ message }}
        vagrant_sdb_data:
          driver: sqlite3
          database: /var/cache/salt/vagrant.sqlite
          table: sdb
          create_table: True

{% if salt['config.get']('vbox_install', false) == true %}
{% if grains.os_family == 'Debian' %}

virtualbox_repo:
  pkgrepo.managed:
  - human_name: virtualbox
  - name: deb http://download.virtualbox.org/virtualbox/debian {{ grains.oscodename }} contrib
  - file: /etc/apt/sources.list.d/virtualbox.list
  - key_url: https://www.virtualbox.org/download/oracle_vbox.asc

virtualbox_packages:
  pkg.installed:
  - names:
    - build-essential
    - dkms
    - linux-headers-{{ grains.kernelrelease }}
    - virtualbox-{{ salt['config.get']('vbox_minor_version') }}
  - skip_verify: true
  - require:
    - pkgrepo: virtualbox_repo

virtualbox_setup_kernel_drivers:
  cmd.wait:
  - name: /etc/init.d/vboxdrv setup
  - cwd: /root
  - watch:
    - pkg: virtualbox_packages

{%- elif grains.os_family == "RedHat" %}

{# TODO #}

{%- elif grains.os_family == "Windows" %}

virtualbox_install_package:
  pkg.installed:
  - name: virtualbox_x64_en

{%- endif %} {# os_family #}

{% set vagrant_version = salt['pillar.get']('vagrant_version', '') %}
{% if vagrant_version != '' %}
{% set vagrant_url = 'https://releases.hashicorp.com/vagrant/' ~ vagrant_version ~ '/vagrant_' ~ vagrant_version ~ '_x86_64.deb' %}
vagrant:
  pkg.installed:
    - sources:
      - vagrant: {{ vagrant_url }}

{% for plugin in salt['pillar.get']('vagrant:plugins', []) %}
vagrant-plugin-{{ plugin }}:
  cmd.run:
    - name: "vagrant plugin install '{{ plugin }}'"
    - unless: "vagrant plugin list | grep '{{ plugin }}'"
{% endfor %}
{% endif %}   {# vagrant_version #}
{%- endif %}  {# vbox_install #}

{% if salt['config.get']('vbox_api_install', false) %}
vbox_sdk:
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

install-vbox-sdk:
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
      - archive: vbox-sdk
    - unless:
      - python -c "import vboxapi"

{% if salt['grains.get']('os_family') == 'Debian' %}
python-pip:
  pkg.installed:
    - names:
      - python-pip
    - require_in:
      - pyvmomi_module
{% endif %}
pyvmomi_module:
  pip.installed:
    - names:
      - pyVmomi    # needed to control VMware packages
    - onlyif:
      {% if salt['grains.get']('os_family') == 'MacOS' %}
      - 'ls /Applications/VMware\ Fusion.app/'
      {% else %}
      - 'which vmrun'
      {% endif %}
{% endif %} {# vbox_api_install #}

sure_minion_config_file:
  file.managed:
    - name: {{ salt['config.get']('salt_config_directory') }}{{ other_minion }}/minion.d/02_configure_bevy_member.conf
    - source: salt://bevy_master/files/02_configure_bevy_member.conf.jinja
    - template: jinja
    - makedirs: true
    - order: 3  {# do this early, before we crash #}

remove_boot_config:
  file.absent:
    - name: {{ salt['config.get']('salt_config_directory') }}/00_vagrant_boot.conf
    - require:
      - file: sure_minion_config_file

{% if other_minion == "" %}
# ... using the stock salt-minion instance #
{{ salt['config.get']('salt_config_directory') }}/minion:
  file.managed:
    - contents: |
        # {{ message }}
        #
        # N.O.T.E. : SaltStack management occurs below this level.
        # The actual work is done in the minion.d directory below this.
        #
    - makedirs: true
    - show_changes: false
    - replace: false
{% else %}  {# other_minion is non-blank #}
# v v v installing a second minion instance to talk with Bevy Master #
{{ salt['config.get']('salt_config_directory') }}{{ other_minion }}/minion:
  file.managed:
    - contents: |
        # {{ message }}
        #
        # This is an empty placeholder file.
        # The actual work is done in the minion.d directory below this.
    - makedirs: true
    - replace: false

# NOTE: this only works on Ubuntu 16.04 and later, and other Linuxes using systemd
make_salt{{ other_minion }}-minion_service:
  file.copy:
    - source: /lib/systemd/system/salt-minion.service
    - name: /lib/systemd/system/salt{{ other_minion }}-minion.service

edit_salt-minion{{ other_minion }}_service:
  file.replace:
    - name: /lib/systemd/system/salt{{ other_minion }}-minion.service
    - pattern: "ExecStart=/usr/bin/salt-minion$"
    - repl: "ExecStart=/usr/bin/salt-minion --config-dir={{ salt['config.get']('salt_config_directory') }}{{ other_minion }}\n"
    - require:
      - file: make_salt{{ other_minion }}-minion_service
    - require_in:
      - service: start-salt{{ other_minion }}-minion

systemctl_reload_{{ other_minion }}:
  service.running:
    - name: salt_minion{{ other_minion }}
    - require:
      - file: edit_salt-minion{{ other_minion }}_service

add_salt{{ other_minion }}_call_command:
  file.append:
    - name: /etc/bash.bashrc
    - text:
      - '# v v v v v v  added by Salt  v v v v v v ( -- Do not edit or remove this line -- )'
      - "alias salt{{ other_minion }}='sudo salt-call --config-dir=/etc/salt{{ other_minion }} \"$@\"'"
      - 'printf ".   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .\\n"'
      - 'printf " * This computer is running a second Salt minion.\\n"'
      - 'printf "\\n"'
      - 'printf " * To use the system Salt master, use the \\\"sudo salt-call\\\" command as usual.\\n"'
      - 'printf "\\n"'
      - 'printf " * For salt-call to the Bevy master, use the \\\"salt{{ other_minion }}\\\" command.  For example:\\n"'
      - 'printf "     salt{{ other_minion }} state.apply saltmine-dump\\n"'
      - 'printf "\\n"'
      - 'printf " * To control the second minion,  use (for example):\\n"'
      - 'printf "     sudo systemctl status salt{{ other_minion }}-minion\\n"'
      - 'printf "\\n"'
      - 'printf " * Normal \\\"sudo salt xxx\\\" commands are for the original Salt Master.\\n"'
      - 'printf ".   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .\\n"'
      - '# ^ ^ ^ ^ ^ ^  added by Salt  ^ ^ ^ ^ ^ ^ ( -- Do not edit or remove this line -- )'


/etc/profile:
  file.append:
    - text:
      - 'source /etc/bash.bashrc  # added by Salt'

{% endif %} # endif other_minion

{% if grains['os_family'] != 'MacOS' %}
start-salt{{ other_minion }}-minion:
  service.running:
    - name: salt{{ other_minion }}-minion
    - enable: true
    - require:
      - file: {{ salt['config.get']('salt_config_directory') }}{{ other_minion }}/minion
    - require_in:
      - cmd: restart-the-minion
{% endif %}

restart-the-minion_1:
  file.managed:
    - name: /tmp/run_command_later.py
    - source: salt://run_command_later.py
    {% if grains['os'] != 'Windows' %}- mode: 775{% endif %}
    - show_changes: false
restart-the-minion:
  cmd.run:
    - bg: true  # do not wait for completion of this command
    - require:
      - file: restart-the-minion_1
    - order: last
    - shell: /bin/bash
    {% if grains['os_family'] == 'MacOS' %}
    - name: '/tmp/run_command_later.py 10 "pkill -f salt-minion"'
    {% elif grains['os_family'] == 'Windows' %}
    - name: 'py \tmp\run_command_later.py 10 net stop salt-minion; net start salt-minion;echo .;echo .;echo "Hit [Enter] to close this window..."'
    {% else %}
    - name: "/tmp/run_command_later.py 10 systemctl restart salt{{ other_minion }}-minion"
    {% endif %}
...
