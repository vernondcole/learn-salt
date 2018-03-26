---
# salt state file for deploying BlackKnight servers
#
install_black_knight:
  pkg.installed:
    - name: black_knight
    - version: "{{ salt['pillar.get']('black_knight:version', 'latest') }}"
...
