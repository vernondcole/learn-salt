## Software installation

_**Remember: Before editing any files in any project,
switch to a new branch in `git`.**_

```
git branch my_edits
git checkout my_edits
```
now ... on to what you really came here for ...

#### MarkDown Viewer

Some of the lesson material in this project (especially the home index)
is in [MarkDown](http://commonmark.org/) format.  The GitHub web site automatically converts MarkDown
(.md) files to html, so that you can read them in your browser within GitHub.

But, you will be downloading the repository to your workstation anyway, and it
makes sense to use your local copy of the lessons.
On your workstation, you will not have the advantage of the GitHub magic, so
you will want to load an addon to your browser to display .md files prettily.


For [Firefox]() try
[MarkDown Viewer](https://addons.mozilla.org/en-US/firefox/addon/markdown-viewer/).

For [Chrome](https://www.google.com/chrome/) try
[this MarkDown Viewer](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk?utm_source=chrome-app-launcher-info-dialog)

To install a native MarkDown reader/editor on your workstation, try
[ReText](https://github.com/retext-project/retext).

#### Salt (after Salt Oxygen is released)

- Linux (and other POSIX systems)
    ```(bash)
    wget  -O bootstrap-salt.sh https://bootstrap.saltstack.com
    # that ^ is a capitol "Oh" not a zero
    sudo sh bootstrap-salt.sh 
    ```

- Everything else

    [See the official Salt page](https://docs.saltstack.com/en/latest/topics/installation/index.html#quick-install)

#### Salt (Oxygen development version, run time)

The Oxygen version of Salt has the modules needed to run Vagrant machines,
and extended features for the `saltify` driver.


- linux (running system, no source code remaining)
    ```(bash)
    wget  -O bootstrap-salt.sh https://bootstrap.saltstack.com
    # that ^ is a capitol "Oh" not a zero
    sudo sh bootstrap-salt.sh git
    ```

- others

    do the full install-from-source below

#### Salt (development copy of source)

refer to [the dirty details here](install_salt_development.md).

#### install Vagrant and Virtualbox (or VMware)

- Ubuntu (and Debian and Raspbian)

  - sudo apt install virtualbox

  - https://www.vagrantup.com/downloads.html

  Add the plugin which keeps VBoxGuestEditions installed and up to date:

  `vagrant plugin install vagrant-vbguest`


- MacOS
To install both packages on *Mac workstations*, you may want to try 
`sh mac_install_vagrant.sh` on the off-chance that I got it right.
If you supply a correction, please consider a pull request.

### Creating a password hash

It is generally a good practice to use a personal account rather than
a generic username. The bevy system is designed to do that.

The bevy master will replicate your username to each bevy minion. Your username will usually be set up for
passwordless sudo and ssh public key login ... but situations may still crop up where you need a password.
For those situations, the Salt scripts will also set a 
[Linux password hash](https://crackstation.net/hashing-security.htm) on each system.

As a source for the Salt Pillar value of your password hash, we will create a hash file in 
your ~/.ssh directory.  The program to do that will be run automatically, or you can run
it stand-alone.
 
**Mac and Windows users NOTE:** You must install Python3  and passlib in order to run pwd_hash.py.

```(bash)
# MacOS #
brew install python3
pip3 install passlib
``` 

```(bash)
cd /projects/learn_salt/configure_machine directory)
./pwd_hash.py
```

### Where to install your bevy master.

It is enterly possible to have a virtual machine (such a VM
bevymaster) host yet more virtual machines. This might not be
the best idea. ([Refer to xkcd](http://xkcd.com/1764).)

Rather, you may elect to use your workstation as the bevymaster so that
it can easily control virtual servers. 
This is the simplest installation, but you may prefer to avoid having
your workstation running Salt master forever.
For these lessons, at least, 
you will want to have your workstation running as a Salt minion.

**Note:** Running a Salt master directly on OS-x is not officially supported 
(see [the docs](https://docs.saltstack.com/en/latest/topics/installation/osx.html).) 
Some OS-x code has been put in the Salt state files, but it may not (yet) be working perfectly. 
Running a salt master on a Linux __virtual__ machine hosted on a MacOS physical machine is fully supported.

In more practical situation, an independant machine may be set up as the Salt master. 
The bevy master machine (wherever located) will configure itself using "salt-call" commands.
It can then spin up or connect the other computers as specified by your settings in its /etc/salt/ directory.

This other machine can be a VM hosted by your workstation,
or a physical or virtual machine elsewhere. 
The system design requires only that each minion must be able to open an IP (UDP) connection
to its Salt master. The master sends commands as replies to minion requests, 
so minions can be inside NAT or other complex routing schemes.

At the start of these lessons, we will assume that you are running your bevy master
on a VM on your workstation.  As the lessons progress, you may want to move it elsewhere.

### Steps to install a bevy master as a VM on your machine.

- Install Vagrant and Virtualbox (as above)

- clone this repository

- run the Python script to configure your workstation and master
  ```bash
    /projects/learn-salt$ cd configure_machine/
    /projects/learn-salt/configure_machine$ ./bootstrap_bevy_member_here.py 
    This program can create either a bevy salt-master (and cloud-master),
    or a simple workstation to join the bevy,
    or a Vagrant host to host the master
    Should this machine be the master? [y/N]:n
    Will the master be a VM guest of this machine? [y/N]:y
    ...
    ```
Continue to answer the configuration questions as appropriate.    

The script should configure both your host and the bevymaster in one operation.
