---
# salt state file for loading Ubuntu via PXE boot server

include:
  - .pxe

ubuntu_tarball:
  archive.extracted:
    - name: /srv/tftpboot/{{ pillar['pxe_netboot_subdir'] }}
    - source: {{ pillar['pxe_netboot_download_url'] }}/netboot/netboot.tar.gz
    - source_hash: {{ pillar['pxe_netboot_download_url'] }}/SHA1SUMS
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

/srv/tftpboot/preseed.files/example.preseed:
  file.managed:
    - source: salt://{{ slspath }}/files/example.preseed
    - makedirs: true
    - template: jinja
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

pxelinux_add_{{ pillar['pxe_netboot_subdir'] }}_option:
  file.append:
    - name: /srv/tftpboot/pxelinux.cfg/default
    - text: |

        label new{{ pillar['pxe_netboot_subdir'] }}
          menu label ^Install new copy of Ubuntu {{ pillar['pxe_netboot_subdir'] }}
          config {{ pillar['pxe_netboot_subdir'] }}pxelinux.cfg/preseed.cfg

/srv/tftpboot/{{ pillar['pxe_netboot_subdir'] }}/pxelinux.cfg/preseed.cfg:
  file.managed:
    - contents: |
        default autobootthis
        prompt 0
        LABEL autobootthis
        KERNEL /{{ pillar['ubuntu_version'] }}/ubuntu-installer/amd64/linux
        IPAPPEND 2  # work around bug
        APPEND vga=788 initrd=/{{ pillar['ubuntu_version'] }}/ubuntu-installer/amd64/initrd.gz auto-install/enable=true preseed/url=tftp://{{ pillar['pxe_server_ip'] }}/preseed.files/example.preseed netcfg/choose_interface=auto
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

create_the_file_clearing_daemon:
  file.managed:
    - name: /srv/tftpboot/preseed.files/file_clearing_daemon.py
    - source: salt://{{ slspath }}/files/file_clearing_daemon.jinja.py
    - template: jinja
    - mode: 775
    - show_changes: false
run_the_file_clearing_daemon:
  cmd.run:
    - bg: true  # do not wait for completion of this command
    - require:
      - file: create_the_file_clearing_daemon
    - shell: /bin/bash
    - name: /srv/tftpboot/preseed.files/file_clearing_daemon.py
let_the_file_clearing_daemon_get_started:
  http.wait_for_successful_query:
    - name: http://{{ pillar['pxe_server_ip'] }}:{{ pillar['pxe_clearing_port'] }}/ping
    - status: 200
    - request_interval: 2
    - wait_for: 20

{% for config in salt['pillar.get']('pxe_netboot_configs') %}
/srv/tftpboot/preseed.files/{{ config['mac'] }}:
  file.managed:
    - source: salt://{{ slspath }}/files/hands_off.preseed
    - template: jinja
    - config_mac: {{ config['mac'] }}
    - makedirs: true
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

/srv/tftpboot/{{ config['subdir'] }}pxelinux.cfg/01-{{ config['mac'] }}:
  file.managed:
    - makedirs: true
    - contents: |
        default autobootnow
        prompt 0
        LABEL autobootnow
        KERNEL {{ config['kernel'] }}
        IPAPPEND 2  # work around bug
        APPEND {{ config['append'] }}{{ config['mac'] }} priority=critical netcfg/choose_interface=auto hostname={{ config['mac'] }}
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

/srv/tftpboot/pxelinux.cfg/01-{{ config['mac'] }}:
  file.managed:
    - makedirs: true
    - contents: |
        default autoboot
        prompt 0

        LABEL autoboot
        CONFIG {{ config['subdir'] }}/pxelinux.cfg/01-{{ config['mac'] }}
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

record_the_file_clearing_data:
  http.query:
    - name: http://{{ pillar['pxe_server_ip'] }}:{{ pillar['pxe_clearing_port'] }}/store?{{ config['mac'] }}?/srv/tftpboot/{{ config['subdir'] }}pxelinux.cfg/01-{{ config['mac'] }}
    - status: 201
{% endfor %}

...
