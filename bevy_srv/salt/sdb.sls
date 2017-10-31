---
# salt state file for setting up Salt's Small DataBase

/etc/salt/master.d/sdb.conf:
  file.managed:
    - source: salt://files/sdb.conf
    - template: jinja
    - onlyif:
      - test -d /etc/salt/master.d

/etc/salt/minion.d/sdb.conf:
  file.managed:
    - makedirs: True
    - source: salt://files/sdb.conf
    - template: jinja
...
