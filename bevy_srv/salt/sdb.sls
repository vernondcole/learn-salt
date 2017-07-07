---
# salt state file for setting up Salt's Small DataBase

bevy_member_grain:
  grains.present:
    - name: roles
    - value:  # a list -- to be appended
      - bevy_member

{% if 'bevy_master' in grains['roles'] %}
/etc/salt/master.d/sdb.conf:
  file.managed:
    - makedirs: True
    - source: salt://files/sdb.conf
    - template: jinja
{% endif %}

/etc/salt/minion.d/sdb.conf:
  file.managed:
    - makedirs: True
    - source: salt://files/sdb.conf
    - template: jinja
...
