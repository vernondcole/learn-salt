---
# salt pillar file for common values for a bevy

{# define module functions which will each minion will run periodically to send data to Salt Mine #}
mine_functions:
  network.ip_addrs: '[]'
  grains.item:
    - fqdn

salt-api:  {# the api server is located using the "master" grain #}
  port: 8000   # TODO: consider using port 4507
  eauth: pam
  username: vagrant
  password: vagrant

bevy_master: '172.17.2.2'
bevy_host: '172.17.2.1'
bevy_dir: '/projects/learn-salt'
...
