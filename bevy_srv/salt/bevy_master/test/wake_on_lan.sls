---
# salt state file for wakening a hardware machine

connect_hw:
  cmd.run:
    - name: 'network.wol'
    - mac: '{{ pillar['wol_test_mac'] }}
...
