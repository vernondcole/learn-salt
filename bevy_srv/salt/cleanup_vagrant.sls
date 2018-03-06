#fs.inotify.max_user_watches:
#  sysctl.present:
#    - value: 1048576

remove_the_competition:  # these take a lot of virtual memory.
  pkg.removed:
    - names:
      - puppet
      - chef

{% if grains['os'] != "Windows" %}
ensure-virt-what:
  pkg.installed:  # gets removed (with puppet) by autoremove
    - name: virt-what
  {% if grains['os_family'] == 'Debian' %}
    - require:
      - pkg.autoremove
pkg.autoremove:
  module.run:
    - order: last
  {% endif %}
{% endif %}
