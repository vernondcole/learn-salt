# file /bevy_srv/pillar/top.sls
#
#   This is an actual pillar top file (not a template) used by the Bevy Master server
#     (on Bevy Master servers where files can be shared with your development workstation)
#     (it will be pulled from the git repo and may be overwritten from it, or pushed to it.)
#
#   In practice, this file will only be used by early "salt-call --local" runs.
#   /srv/pillar/top.sls will be the real thing.
#
# The Bevy Master is expected to be run with a /etc/salt/master.d/??? configuration like:
# pillar_root:
#   - /srv/pillar
#   - /bevy_srv/pillar
# pillar_source_merging_strategy: recurse    # merge data from all pillar sources
#
# make local modifications in /srv/pillar/???
#
base:
  '*':
    - core_settings  # all systems share these
    - my_user_settings  # found in /srv/pillar

  'quail*':
    - demo_bevy_settings

  bevymaster*:
    - demo_bevy_settings

  'bevy:*':
    - match: grain
    - demo_bevy_settings
