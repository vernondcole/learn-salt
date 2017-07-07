#fs.inotify.max_user_watches:
#  sysctl.present:
#    - value: 1048576

remove_the_competition:  # these take a lot of virtual memory.
  pkg.removed:
    - names:
      - puppet
      - chef

ensure-virt-what:
  pkg.installed:  # gets removed (with puppet) by autoremove
    - name: virt-what
{% if salt['grains.get']('os_family') == 'Debian' %}
    - require:
      - pkg.autoremove
pkg.autoremove:
  module.run:
    - order: last
{% endif %}
