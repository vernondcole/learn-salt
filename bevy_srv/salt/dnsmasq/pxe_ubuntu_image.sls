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
    - source: salt://dnsmasq/files/example.preseed
    - makedirs: true
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff

{% for config in salt['pillar.get']('pxe_netboot_configs') %}
/srv/tftpboot/{{ config['subdir'] }}pxelinux.cfg/01-{{ config['mac'] }}:
  file.managed:
    - makedirs: true
    - contents: |
        default autoboot
        prompt 0

        LABEL autoboot
        KERNEL {{ config['kernel'] }}
        APPEND {{ config['append'] }}

    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff
{% endfor %}
...
