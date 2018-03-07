# {{ pillar['salt_created_message'] }}
# {# also the top for the initial creation of the bevy master #}
base:
  '*':
    - common
    - administrator_user
    - interactive_user
    - cleanup_vagrant
    - ensure_user_privs
    # - sdb

  bevymaster:
    - bevy_master.define_interactive_user
    - bevy_master
    - bevy_master.local_windows_repository  # false negative: reports an error which does not occur.

