---
# salt state file for reconfiguring a hardware machine


include:
  - dnsmasq.pxe_auto_install

start_hw:
  module.run:
    - name: network.wol
    - mac: {{ pillar['wol_test_mac'] }}

connect_to_bevy:
#  cloud.profile:
#    - name: x_hw
#    - profile: hw_demo
  cmd.run:
    - name: salt-cloud -p hw_demo x_hw --log-level=info
...
