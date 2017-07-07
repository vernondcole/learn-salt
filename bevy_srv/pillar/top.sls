# file /bevy_srv/pillar/top.sls
#
#   This is the actual pillar top file (not a template) used by the Bevy Master server
#     (on Bevy Master servers where files can be shared with your development workstation)
#     (it will be pulled from the git repo and may be overwritten from it, or pushed to it.)
#
# The Bevy Master is expected to be run with a /etc/salt/master.d/??? configuration like:
# pillar_root:
#   - /bevy_srv/pillar
#   - /srv/pillar
# pillar_source_merging_strategy: recurse    # merge data from all pillar sources
#
# make local modifications in /srv/pillar/???
#
base:
  '*':
    - common  # all systems share these

  'quail*':
    - bevy_settings
    - my_user_settings  # found in /srv/pillar

  bevymaster:
    - bevy_settings
    - my_user_settings
