# file /bevy_srv/pillar/top.sls
#
#   This is the actual pillar top file (not a template) used by the Bevy Master server
#     (on Bevy Master servers where files can be shared with your development workstation)
#     (it will be pulled from the git repo and may be overwritten from it, or pushed to it.)
#
# The Bevy Master is expected to be run with a /etc/salt/master.d/??? configuration like:
# pillar_root:
#   - /learn-salt/pillar
#   - /projects/black_knight/local_salt/pillar
#   - /srv/pillar
# pillar_source_merging_strategy: recurse    # merge data from all pillar sources
#
# make local modifications in /srv/pillar/???
#
base:
  '*':
    - core_settings  # all systems share these
    - bevy_settings
    - 01_bootstrap_settings  # found in /srv/pillar as written by bootstrap....py
    - black_knight_settings
