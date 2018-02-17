Installing third-party packages
===============================
On your Bevy Master, run the command to load your Windows package definitions.
See the Salt instructions for [Windows Software Repository](https://docs.saltstack.com/en/latest/topics/windows/windows-package-manager.html)

Then package management can be used on Windows minions.
For example, to install firefox on node win16:
* `sudo salt-run winrepo.update_git_repos`
* `sudo salt win16 pkg.install firefox`
