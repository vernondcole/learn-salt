---
# salt state file for all systems

{% if grains['os_family'] != 'Windows' %}

{% if grains['mem_total'] < 2000 %}
swapspace:
  pkg.installed:
    - refresh: true
    - cache_valid_time: 600
    - order: 1
{% endif %}

{% if salt['grains.get']('os_falmily') == 'Debian' %}
  pkg.installed:
    - pkgs:
      - git
      - htop
      - mtr
      - nano
      - tree
{% endif %}

{% if salt['grains.get']('os') == 'Ubuntu' %}
common_packages:
  pkg.installed:
    - pkgs:
      - jq
      - python-software-properties
      - silversearcher-ag
      - strace
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
{% endif %}
...
