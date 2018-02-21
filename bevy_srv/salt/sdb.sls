---
# salt state file for setting up Salt's Small DataBase

{{ pillar['salt_config_directory'] }}/master.d/sdb.conf:
  file.managed:
    - source: salt://files/sdb.conf
    - template: jinja
    - onlyif:
      - test -d {{ pillar['salt_config_directory'] }}/master.d

{{ pillar['salt_config_directory'] }}/minion.d/sdb.conf:
  file.managed:
    - makedirs: True
    - source: salt://files/sdb.conf
    - template: jinja
...
