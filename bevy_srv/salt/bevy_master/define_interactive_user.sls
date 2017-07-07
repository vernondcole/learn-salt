---
# salt state file for putting the interactive user's info into the master data scripts.

{% set my_linux_user = salt['config.get']('my_linux_user') %}

/srv/pillar/my_user_settings.sls:
  file.managed:
    - makedirs: true
    - group: staff
    - mode: 664
    - source: salt://bevy_master/user_settings.pillar.jinja
    - template: jinja
    - order: 2

# salt state file to place creator's public key on bevy master server
# assumes that Vagrant (or somebody) has mapped the /my_home/.ssh directory

establish_my_pub_key:
  file.managed:
    - name: /srv/salt/ssh_keys/{{ my_linux_user }}.pub
    - source: /my_home/.ssh/id_rsa.pub
    - makedirs: true
    - order: 3
    - onlyif:
      - test -e /my_home/.ssh/id_rsa.pub
...
