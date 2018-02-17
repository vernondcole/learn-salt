---
# salt state file to ensure user's priviledges on a virtual machine

{% set my_user = salt['pillar.get']('my_linux_user') %}
{% set home = 'C:/Users/' if grains['os'] == "Windows" else '/home/' %}

include:
  - interactive_user

{{ home }}{{ my_user }}/.ssh:
  file.directory:
    - user: {{ my_user }}
    {% if grains['os'] != "Windows" %}
    - group: {{ my_user }}
    - dir_mode: 755
    {% endif %}

ssh_public_key:
  ssh_auth.present:
    - user: {{ my_user }}
    - source: salt://ssh_keys/{{ my_user }}.pub
    - require:
      - file: {{ home }}{{ my_user }}/.ssh

{% if grains['os'] != "Windows" %}
/etc/sudoers:  # set the interactive linux user for passwordless sudo
  file.append:
    - text: |
        {{ my_user }} ALL=(ALL) NOPASSWD: ALL
{% endif %}
...
