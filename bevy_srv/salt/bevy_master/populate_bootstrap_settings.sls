---
# salt state file for putting the bootstrap info into the master data scripts.
# this operation is critical when the bevy master is created by 'vagrant up'
#
{# this file should only be written during a bootsrapping run #}
{% if salt['pillar.get']('doing_bootstrap', false) %}
/srv/pillar/01_bevy_settings.sls:
  file.managed:
    - makedirs: true
    {# NOTE: cannot define user here, user has not yet been created #}
    - mode: 664
    - source: salt://bevy_master/files/bootstrap_settings.pillar.jinja
    - template: jinja
    - order: 2  # do this before something crashes Salt processing
{% endif %}
