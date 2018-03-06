##### Pre-created minions using Saltify provider.

The salt-cloud "saltify" provider is used to connect hardware machines, or
virtual machines (not created by salt-cloud) as bevy member minions.
It installs salt-minion on the target machine and connects it to the bevy master with the appropriate keys. 
The target machine is then ready to run any Salt command, including state.highstate.

The definition of all machines to be connected to your bevy is found in the 
/etc/salt/cloud.profiles.d/ directory. That directory is initially populated by a Salt file.recurse
 operation which will overwrite any file found in its source directory, which is
 `/bevy_srv/salt/bevy_master/cloud.profiles.d`. The saltify_demo_profiles.conf file contains the
demo or default examples.  To avoid having Salt overwrite
 your own machine definitions, you should make a new `.conf` file with a different name. 
