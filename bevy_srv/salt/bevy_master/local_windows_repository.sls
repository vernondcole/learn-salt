---
# Salt state for using a local source for Windows software definitions
# - - - this state is to run on the Salt Master
#
/srv/salt/win/repo-ng:
  file.directory:
    - makedirs: true

# Sample: use a local definition to find Notepad++
/srv/salt/win/repo-ng/npp.sls:
  file.managed:
    - source: salt://bevy_master/files/npp.sls.source
...
