# minimal "top.sls" file to create a new SaltStack master
#
base:
  '*':
    - common

  'x_*':
    - interactive_user
    - cleanup_vagrant
    - ensure_user_privs
    - black_knight

  bevymaster:
    - interactive_user
    - bevy_master

