# learn-salt

#### (Using salt-cloud to learn SaltStack basics)

This project uses a salt-cloud network with Vagrant-powered VirtualBox virtual machines as a sandbox to experiment with and learn [Salt](https://saltstack.com/) and [salt-cloud](https://docs.saltstack.com/en/latest/topics/cloud) by building and controlling a bevy of computers.

### Installation

Clone [1] [this git repository](https://github.com/vernondcole/learn-salt) onto your target environment --
which should be the workstation where you plan to do the lessons. You will control your bevy
from this place.

Place it in the `/projects/learn-salt` directory[2]. Or not -- you don't really have to put it there. All lessons should work if you put it somewhere else, like `/home/myusername/learn` or wherever. 
Examples will be configured and tested to operate from any random directory you like.  
But, for simplicity sake, all examples will be given as if they were in `/projects/learn-salt`.

Before editing any files in this project,
please switch to a new branch in `git`.

```
git branch my_edits
git checkout my_edits
```
If you need to return to the original text, you can use `git`
to restore it.
`git checkout master`

[1]: see [how to git stuff](lessons/git/how_to_git_stuff.md) if you don't understand what "clone" means.

[2]: Windows users -- use the `C:\projects\learn-salt` folder. All future instructions will use POSIX names with right-leaning slashes and no drive letter. Live with it. If you need help, look in the [Linux for Windows Users](lessons/windows/Linux_for_Windows_users.md) lesson.


### What the #&*$%! is a `bevy`?

In this project, we will use the term "bevy" to specify the collection of virtual (and sometimes physical) computers which are managed by our Salt master.

The Oxford English dictionary says:

```
    bev·y  ˈbevē
    noun
       a large group of people or things of a particular kind.
```

A bevy might have more than one master (if we are experimenting with multi-master arrangements) but each master (or set of masters) will control only one bevy. The machines in the bevy may reside on any number of IP networks.

#### Why not just call it a `<fill in the blank>` rather than a `bevy`?

Most collective nouns are already used in computer science jargon. "Network" has several meanings -- so does "array", "collection", "cluster", "group", "quorum", "environment" and so on. The thesarus was searched for a unique, unused term. 
"Bevy" is a collective noun used for quail. (Other terms are "covey" and "flock".)
Being a part-time hunter and full-time westerner, I (Vernon) admire the way a group of quail co-operate together. (They are [very pretty](https://www.pfwebsites.org/chapter/snakeriverqforg/photos/002.jpg), too.) So I decided to adopt that term for a co-operating group of computers.  Blame me.

Feel free to substitute some other word if you prefer.

### How this project is arranged.

This directory has this README.md file,
along with a big complex *Vagrantfile*,
and a few other handy files.

The [lessons](./lessons) directory contains 
the [lesson index](lessons/index.md).

[comment]: # (The file index.md is the source for index.html)

The [bevy_srv](./bevy_srv) directory contains a complete SaltStack
directory tree used for building the examples and lessons here.

The [configure_machine](./configure_machine) directory contains 
scripts usesd to configure your bevy_master machine, your workstation
(as a minion), and perhaps other bevy member computers as needed.

### How to read the text and lessons.

Various lessons may appear in different formats as dictated by time, the complexity of the
content, and the whim of the author.  Possibilities will include 
[SMART notebooks](https://education.smarttech.com/products/notebook),
[open document (.odp) presentations](http://www.libreoffice.org/discover/impress/), 
html web pages, or markdown pages (like this one.)

You should always be able to read the lessons directly from the links on GitHub --
but will probably have a better experience if you install software on your own
workstation to display the documents locally. Lessons are provided for installing
appropriate programs on Windows and MacOS as well as Linux.  The Linux examples
will assume Ubuntu (or another Debain-based distro such as Raspbian.) If you use a 
different POSIX system, we hope that you are fimiliar with the translation from
Debian commands (apt) to your preferred OS's way of saying the same thing (yum, zypper, 
emerge). *NIX and *BSD users are also invited to read the Linux pages and translate.

Sample shell scripts are provided like

```
    # this is a shell script sample.
    # it should be simple enough to operate on almost any shell language,
    # such as bash, git-bash (on Windows), sh, dash, etcetera.
    ls -al
    echo $PATH
    # you may cut them out and paste them into your command terminal,
    # but you might learn better if you type them with your own fingers.
```

v v v v v v v v v v Text below should be moved to individual class lessons v v v v

Each machine is automatically connected to and accepted by your salt master.
https://github.com/vernondcole/learn-salt


### Decide where to install your bevy master.


It is enterly possible to have a virtual machine (such a VM
bevymaster) host yet more virtual machines. This might not be
the best idea. ([Refer to xkcd](http://xkcd.com/1764).) You may
elect to use your workstation as the bevymaster so that it can easily
control virtual servers.
https://github.com/vernondcole/learn-salt

In more practical situation, an independant machine may be set up as the Salt master. 
The bevy master machine (wherever located) will configure itself using "salt-call" commands.
It can then spin up or connect the other computers needed for the dynamux environment as specified by your settings in the /etc/salt/ directory.

**Note:** Running a Salt master directly on OS-x is not officially supported 
(see [the docs](https://docs.saltstack.com/en/latest/topics/installation/osx.html).) 
Some OS-x code has been put in the Salt state files, but it may not (yet) be working perfectly. 
Running a salt master on a Linux __virtual__ machine hosted on a MacOS physical machine is fully supported.

### Steps to install a bevy master as a VM on your machine.


First, install git, if needed, and set your worstation
up on the github server `http://p-bitbucket.imovetv.com`

##### clone this repository to intended host machine

```

cd /projects  # go to your project directory, this is an example
git clone ssh://git@p-bitbucket.imovetv.com/msl/bevy_master.git
cd bevy_master
```

#### install Vagrant and Virtualbox (or VMware)

To install both packages on Mac workstations, you may want to try 
`sh mac_install_vagrant.sh` on the off-chance that I got it right.
If you supply a correction, please consider a pull request.

For Ubuntu:

- Refer to https://www.virtualbox.org/wiki/Downloads .

- https://www.vagrantup.com/downloads.html

Add the plugin which keeps VBoxGuestEditions installed and up to date:

`vagrant plugin install vagrant-vbguest`


##### create a password hash

The bevy master will replicate your username to each bevy minion. Your user will usually be set up for
passwordless sudo and ssh public key login ... but situations may still crop up where you need a password.
For those situations, the Salt scripts will also set a 
[Linux password hash](https://crackstation.net/hashing-security.htm) on each system.

As a source for the Salt Pillar value of your password hash, we will create a file in the ~/.ssh directory on
your workstation. The value will then be passed to your bevy master during `vagrant up`. 

 
**Mac and Windows users NOTE:** You must install Python3  and passlib in order to run pwd_hash.py.

```
(bash)
# Mac only #
brew install python3
pip3 install passlib
``` 

```
(bash)
# \(... assuming you are in the /projects/learn_salt directory or its equivalent on your system ...)
./configure_machine/pwd_hash.py
```

##### modify Vagrantfile to your exact wishes

Use the editor of your choice to customize the nascant virtual machine as desired.

`nano Vagrantfile`

##### Start your bevy master VM and connect a terminal session to it. 

`vagrant up` or `vagrant up --provider vmware_fusion`

`vagrant ssh`

##### Start a bevy minion VM, control it, and connect a terminal session to it. 

(In the examples below, subistitute 'quail14' to run an Ubuntu 14.04 machine.)

`vagrant up quail16` or `vagrant up quail16 --provider vmware_fusion`

NOTE: you must use the same VM provider on all machines. Mixing VirtualBox and VMware machines messes up networking.

```(bash)
me@myhost$ vagrant ssh
...
me@bevymaster $ sudo salt-cloud -p quail16 myminion
me@bevymaster $ sudo salt myminion network.ip_addrs
```

`me@bmyhost $ vagrant ssh quail16`

or

`me@anymachine $ ssh 10.<ip address from above>`

### Steps to use a VMware GP2 cloud machine as your bevy master.
 
Define a small virtual machine (1 CPU, 1GB RAM) on [Javelin](https://d-gp2-javelin2-1.imovetv.com). 
For "App Name" use the word "bevy" followed by a number. The number you pick cannot be the same as an existing bevy.

Log in to your Bevy-Master-to-be using the user name assigned by dev-ops.  Mine is "VCole". Then download the
bevy master repository.  For move explananion of the steps, refer to the "external VM" section below.

```(bash)
ssh-add -K  # Mac only -- starts authentication agent
ssh -A vcole@d-gp2-bevy2-1.imovetv.com`  # -A means "forward my agent authentication"
sudo mkdir /projects
sudo chown vcole:staff /projects
git clone ssh://git@p-bitbucket.imovetv.com/msl/bevy_master.git
cd bevy_master/configure_machine/
sudo ./bootstrap_bevy_member_here.pyhttps://github.com/vernondcole/learn-salt

Using [salt-cloud](https://docs.saltstack.com/en/latest/topics/cloud/index.html),
you will create, manage, and destroy virtual computers.
You will also integrate and control physical machines using the 
[Saltify](https://docs.saltstack.com/en/latest/topics/cloud/saltify.html) driver
Name your bevy: {'bevy1'}: bevy2  # type the same bevy number you selected above

User Name: elmerfudd  # type the user name you use on your workstation
```

The remaining interactive script should be self explanitory.  The python script will run a Salt highstate.
After the highstate completes, you should log off the ssh session and log back in with your workstation 
user name.

N O T E : The script will install a second Salt Minon. The normal salt minion will be connected to the GP2
salt master. The second minion will be connected to the Bevy Master. Its service name will be salt2-minion.
A bash alias named "salt2" is defined for convenient operation of the second minion.
https://github.com/vernondcole/learn-salt
### Steps to use an external VM (or a workstatio
Using [salt-cloud](https://docs.saltstack.com/en/latest/topics/cloud/index.html),
you will create, manage, and destroy virtual computers.
You will also integrate and control physical machines using the 
[Saltify](https://docs.saltstack.com/en/latest/topics/cloud/saltify.html) drivern) as your bevy master.
 
Your proposed bevy master must be running an ssh server (unless it _is_ your workstation).
 `sudo apt install openssh-server`

Your local workstation must have a registered 
[ssh public key](https://confluence.atlassian.com/bitbucketserver0413/using-ssh-keys-to-secure-git-operations-873874478.html)
 on [p-bitbucket.imovetv.com](http://p-bitbucket.imovetv.com:7990).
 
- Log in to your proposed Salt Master using ssh agent forwarding.

```(bash)
    ssh-add -K ~/.ssh/id_rsa    # needed once per reboot, only on Mac OS-x, to register your key with your agent
    ssh -A <target_username>@<your proposed master>
    ```https://github.com/vernondcole/learn-salt

- Decide on your project root directory.  I find it very convenient to create:

    ```  
    (bash)
    sudo mkdir /projects
    sudo chown <your username>:staff /projects
    ```

- Clone this repo onto your intended master using git.

    ``` (bash)
    sudo apt install git  # if needed...
    cd /projects  # go to your project directory
    git clone ssh://git@p-bitbucket.imovetv.com/msl/bevy_master.git
    cd bevy_master
    ```

- run scripts to install all the files and directories.

    ```
    (bash)
    # assuming you are in the bevy_master directory...
    cd configure_member
    sudo ./bootstrap_bevy_member_here.py
    ```

Be prepared to supply the username, password, and ssh public key you wish to have installed on the bevy master and on all of the bevy minions.
This should be your dish user name.  Salt will also create the standard "vagrant" user on all minions.

If the script detects a minion connected to another Salt master 
(not localhost) it will install a second minion to connect its local Salt master.

#### Create other Virtual Minions

For more information, see
https://docs.saltstack.com/en/latest/topics/cloud/qs.html

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

^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^

# Updating this project.

 If you wish to customize or improve this project, create a fork of the source.
 In [the source repository](https://github.com/vernondcole/learn-salt)
 you should see a `Fork` button in the upper right corner.  Click it.

 To submit updates, please follow the flow used for SaltStack, as suggested in
 [Developing Salt](https://docs.saltstack.com/en/latest/topics/development/contributing.html#sending-a-github-pull-request).

Compile markdown (.md) files into .html using [ReText](https://github.com/retext-project/retext)
