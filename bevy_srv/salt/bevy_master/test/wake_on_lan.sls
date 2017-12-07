---
# salt state file for wakening a hardware machine

{% if grains['id'] == pillar['wol_test_sender_id'] %}
connect_hw:
  module.run:
    network.wol
      - mac: {{ pillar['wol_test_mac'] }}
{% endif %}
...
