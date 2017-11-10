---
# salt pillar file for common values for a bevy

{# define module functions which will each minion will run periodically to send data to Salt Mine #}
mine_functions:
  network.ip_addrs: '[]'
  grains.item:
    - fqdn

#change to agree with your actual saltify test hardware machine
wol_test_machine_ip: 192.168.88.8  # the ip address of the minion machine
wol_test_mac: '00-1a-4b-7c-2a-b2'  # ethernet address of minion machine
wol_test_sender: pizero  # node name of WoL transmitter
pxe_network: '192.168.88.0/24'
bevymaster_bridged_ip: 192.168.88.4
bevymaster_hostonly_ip: 172.17.2.2
bevy_host_id: 'vc-ddell'
bevy_dir: '/projects/learn-salt'
vagrant_bridge_target_network: '192.168.88.0/24'
#

salt-api:  {# the api server is located using the "master" grain #}
  port: 8000   # TODO: consider using port 4507
  eauth: pam
  username: vagrant
  password: vagrant

  tls_organization: 'My Company Name'
  tls_location: 'Somewhere, UT'
  tls_emailAddress: 'me@mycompany.test'
...
