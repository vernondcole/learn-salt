---
# salt state file for reconfiguring a hardware machine


include:
  - dnsmasq.pxe_auto_install

start_hw:
  module.run:
    - name: network.wol
    - mac: {{ pillar['wol_test_mac'] }}
...
