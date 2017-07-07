---
# salt state file for installing the SaltStack netAPI server components
#    https://docs.saltstack.com/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html
include:
  - bevy_master
  - pepper

salt-api:
  pkg.installed:
    - unless:
      - salt-api --version

cherrypy:
  pip.installed:
    - names:
      - CherryPy == 8.7.0
      - pyOpenSSL == 16.2.0
      - ws4py

create-cert:
  module.run:
    - name: tls.create_self_signed_cert
    - kwargs:
      - O: 'Sling TV'
      - L: 'American Fork'
      - emailAddress: {{ salt['config.get']('my_linux_user') }}@sling.com # will not really work

/etc/salt/master.d/api.conf:
  file.managed:
    - makedirs: True
    - source: salt://bevy_master/files/api.conf
    - template: jinja

salt-api-service:
  service.running:
    - name: salt-api
    - enable: True
    - watch:
      - pkg: salt-api
      - file: /etc/salt/master.d/api.conf
    - require:
      - delay_master_restart
...
