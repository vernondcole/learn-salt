---
# salt state file to ensure user's priviledges on a virtual machine

# assumes that Vagrant (or somebody) has mapped the /my_home/.ssh directory
{% set my_linux_user = salt['pillar.get']('my_linux_user') %}

include:
  - interactive_user

/home/{{ my_linux_user }}/.ssh:
  file.directory:
    - user: {{ my_linux_user }}
    - group: {{ my_linux_user }}
    - dir_mode: 755

ssh_public_key:
  ssh_auth.present:
    - user: {{ pillar["my_linux_user"] }}
    - source: salt://ssh_keys/{{ my_linux_user }}.pub
    - require:
      - file: /home/{{ my_linux_user }}/.ssh

/etc/sudoers:  # set the interactive linux user for passwordless sudo
  file.append:
    - text: |
        {{ my_linux_user }} ALL=(ALL) NOPASSWD: ALL
...
