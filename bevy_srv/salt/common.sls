---
# salt state file for all systems
{% if grains['os_family'] == 'Windows' %}

pkg.refresh_db:
  module.run:
  - require_in:
    - pkg: windows_packages

windows_packages:
  pkg.installed:
    - pkgs:
      - npp

{% else %}
{% if grains['mem_total'] < 2000 %}
swapspace:
  pkg.installed:
    - refresh: true
    - cache_valid_time: 600
    - order: 1
{% endif %}

{% if grains['os_family'] == 'Debian' %}
debian_packages:
  pkg.installed:
    - pkgs:
      - git
      - htop
      - mtr
      - nano
      - tree
{% endif %}

{% if salt['grains.get']('os') == 'Ubuntu' %}
ubuntu_packages:
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
