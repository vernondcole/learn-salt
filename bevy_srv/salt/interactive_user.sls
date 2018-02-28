---
# salt state file to define an interactive user, used in development.
#
{% set make_uid = salt['config.get']('my_linux_uid', -2) | int %}  {# does not force uid if blank #}
{% set make_gid = salt['config.get']('my_linux_gid', -2) | int %}
{% set my_user = pillar['my_linux_user'] %}
{% set home = 'C:/Users/' if grains['os'] == "Windows" else '/home/' %}
{% set users = 'Users' if grains['os'] == "Windows" else 'users' %}

{% if not salt['file.directory_exists'](home + my_user + "/Desktop") %} {# do not do this on user's workstation #}
staff:
  group:
  - present

{{ my_user }}:
  user:
    - present
    - groups:
    {% if grains['os'] == 'Windows' %}
      - Administrators {% else %}
      - sudo{% endif %}
    - optional_groups:
      - {{ users }}
      - www-data
      - staff
      - dialout
      - wireshark
    {% if grains['os'] == 'Windows' %}
    - home: 'C:\\Users\\{{ my_user }}'
    #- win_homedrive: 'C:'
    {% elif grains['os'] == 'MacOS' %}
    - home: '/Users/{{ my_user }}'
    {% endif %}
    {% if grains['os'] != 'Windows' %}
    - shell: /bin/bash
    - password: "{{ salt['pillar.get']('linux_password_hash') }}"
    - enforce_password: {{ salt['config.get']('force_linux_user_password', false) }}
    {% if make_uid > 0 %}- uid: {{ make_uid }} {% endif %}
    {% endif %}

{% if grains['os'] == 'Windows' %}
'C:\\Users\\{{ my_user }}':
  file.directory:
    - user: {{ my_user }}
    - recurse:
      - user
{% elif grains['os'] == 'MacOS' %}
'/Users/{{ my_user }}':
  file.directory:
    - user: {{ my_user }}
    - recurse:
      - user
{% endif %}
{% endif %}
...
