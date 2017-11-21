---
# salt state file for loading Ubuntu via PXE boot server

include:
  - pxe

tftp_dir:
  file.directory:
    - name: /srv/tftpboot
    - user: {{ salt['config.get']('my_linux_user') }}
    - group: staff
    - dir_mode: 775
    - file_mode: 644
    - makedirs: true

supply_memtest_bin:
  file.managed:
    - name: /srv/tftpboot/memtest86+  # NOTE: no ".bin"
    - source:
      - /boot/memtest86+.bin
      - salt://{{ slspath }}/files/memtest86+.bin
    - use: {file: tftp_dir}

/srv/tftpboot/pxelinux.cfg/default:
  file.managed:
    - makedirs: true
    - contents: |
        default memtest86
        prompt 1
        timeout 15

        label memtest86
          menu label Memtest86+
          kernel /memtest86+

/srv/tftpboot/pxelinux.0:
  file.copy:
    - source: /usr/lib/PXELINUX/pxelinux.0

/srv/tftpboot/ldlinux.c32:
  file.copy:
    - source: /usr/lib/syslinux/modules/bios/ldlinux.c32

/etc/dnsmasq.d/dnsmasq_pxe.conf:
  file.managed:
    - source: salt://{{ slspath }}/files/dnsmasq_pxe.conf
    - template: jinja
    - makedirs: true

/etc/default/dnsmasq:
  file.append:
    - text: "DNSMASQ_EXCEPT=lo  ## Added by Salt"

dnsmasq_service:
  service.running:
    - name: dnsmasq
    - enable: true
    - watch:
      - file: /etc/default/dnsmasq
      - file: /etc/dnsmasq.d/dnsmasq_pxe.conf
      - pkg: dnsmasq
...
