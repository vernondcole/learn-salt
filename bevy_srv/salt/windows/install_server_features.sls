---
# Salt state for installing Windows server features
#
# Install multiple features, exclude the Web-Service
install_multiple_features:
  win_servermanager.installed:
    - recurse: True
    - features:
      - RemoteAccess
      - XPS-Viewer
      - SNMP-Service
    - exclude:
      - Web-Service
...
