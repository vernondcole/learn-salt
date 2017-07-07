# minimal "top.sls" file to create a new SaltStack master
#
base:
  '*':
    - common
    - define_ipv6_local
    - administrator_user
    - interactive_user
    - cleanup_vagrant
    - ensure_user_privs
    - sdb

  bevymaster:
    - bevy_master.define_interactive_user
    - bevy_master
    - helper_scripts
