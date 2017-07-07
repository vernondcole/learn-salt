---
# salt state file for all systems

identify_self:
  module.run:
   - name: config.get
   - kwargs:
     key: id

{% if salt['grains.get']('os') == 'Ubuntu' %}
common_packages:
  pkg.installed:
    - pkgs:
      - git
      - htop
      - jq
      - mtr
      - nano
      - python-software-properties
      - silversearcher-ag
      - strace
      - tree
      - vim-tiny
      - virt-what
      {% if grains['osrelease'] < '16.04' %}
      - python-git  # fallback package if pygit2 is not found.
      {% else %}
      - python-pygit2
      {% endif %}
      {% if grains['locale_info']['defaultlanguage'] != 'en_US' %}
      - 'language-pack-en'
      {% endif %}
{% endif %}
...
