---
# salt state file to define an interactive Linux user, used in development.
#

{% set make_uid = salt['config.get']('my_linux_uid', -2) | int %}  {# does not force uid if blank #}
{% set make_gid = salt['config.get']('my_linux_gid', -2) | int %}
{% set my_user = pillar['my_linux_user'] %}


staff:
  group:
    - present
    - require_in:
      - user: {{ my_user }}

{{ my_user }}:
  group:
    - present
    {% if make_gid > 500 %}- gid: {{ make_gid }} {% endif %}
    - unless:
      - test -e /home/{{ my_user }}/Desktop
  user:
    - present
    - shell: /bin/bash
    - groups:
      - {{ my_user }}
      - users
      - sudo
    - optional_groups:
      - www-data
      - staff
      - dialout
    - password: "{{ salt['pillar.get']('linux_password_hash') }}"
    - enforce_password: {{ salt['config.get']('force_linux_user_password', false) }}
    {% if make_uid > 0 %}- uid: {{ make_uid }} {% endif %}
    - require:
      - group: {{ my_user }}
    - unless:
      - test -d /home/{{ my_user }}/Desktop  {# do not alter a workstation user's information #}
...
