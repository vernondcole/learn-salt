# learn-salt

### Using salt-cloud to learn SaltStack basics

This project uses a salt-cloud network with Vagrant controlled VirtualBox virtual machines as a sandbox to experiment with and learn [Salt](https://saltstack.com/) and [salt-cloud](https://docs.saltstack.com/en/latest/topics/cloud) by building and controlling a bevy of computers.

Go to [the Lesson index](lessons/index.md).

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

Proceed with the instructions in [the installation lesson](lessons/installation/install.md).

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

Often, the lessons will have lab or example files
associated with them. When studying each lesson, you should be running the examples using
a terminal with your current default directory set for that lesson.
For example, if you are running the [Basics of Vagrant](vagrant_basics/basics_of_vagrant.md)
lesson, you should start by running: 

`cd /projects/learn-salt/lessons/vagrant_basics`


[comment]: # (The file index.md is the source for index.html)

The [bevy_srv](./bevy_srv) directory contains a complete SaltStack
directory tree used for building the examples and lessons here.

The [configure_machine](./configure_machine) directory contains 
scripts used to configure your bevy_master machine, your workstation
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

### Vagrant VMs on your workstation

A Vagrantfile is supplied here to create several virtual machines on your workstation. 
(Some lessons may also have a Vagrantfile for that lesson.)

You can create a Salt cloud master ("bevymaster") as a virtual machine on your workstation.
This can be very convenient, except for **one restriction** which occurs if you have any 
application servers (salt minions) running separately from your workstation. 
Minions will be trying to connect to their master at a fixed address. 
If your master should re-connect using a different IP address, they will be lost. 
You will need to consistently use the same network connection for your host workstion,
or use some sort of dynamic DNS arrangement.

The Vagrantfile also defines two simple empty Ubuntu 16.04 VMs, named "quail1" and "quail16".
  
There is also an Ubuntu 14.04 VM (named "quail14") defined in the Vagrantfile. 

Finally, there is a VM named "quail42" for quick-and-dirty operation which will be configured as a Salt minion.

Each of these has three virtual network ports:

- One has a pre-defined IP address range used
for a Vagrant host-only network adapter, 
which used to connect a virtual directory, 
as the address Vagrant uses to ssh connect to the machines,
and for NAT networking from the VM to the world. 
As supplied, these will be subnets of 172.17.17.0.

- A second has a fixed hard-wired address for a
[private network](https://www.vagrantup.com/docs/networking/private_network.html) 
which can be used for intercommunication between the host and its virtual machines 
(and the VMs to each other) but cannot be seen outside the host environment.
These will be in the 172.17.2.0 network, with the host at 172.17.2.1.

- The third is a [bridged network](https://www.vagrantup.com/docs/networking/public_network.html) 
which makes the VM appear to be on the same LAN segment as its host. 
The address for this adapter will be assiged by DHCP. You may need to modify the configuration
parameter `network_mask` to help the scripts discover the actual address.
This port can be seen by machines on your in-house network.  
Be aware that, depending on router configuration settings, VMs on your machine may be
unable to access brother VMs using their bridged ports.

If you wish, you can add more local VMs by editing the Vagrantfile.

Vagrant requires the name of the interface which will be used for a bridged network.
Since a workstation usually has more than one interface (are you using WiFi or hard wire?)
this can be trick to determine. Vagrant will ask the user for input.
There is a messy bunch of Ruby code in the Vagrantfile to try getting the correct name.
You may want to supply your network adapter name in the Vagrantfile, 
especially if you are running Windows.

### A Private Test Network

Some of the more advanced lessons (such as DHCP and PXE) cannot be run on a corporate or
school network without messing up many things. Don't do that. 
\[Trust me -- I once killed the then-experimental
Internet in all of Utah and Colorado with a router misconfiguration.\] 

If you are working from a home office, you will be okay testing on your home router -- 
but not while your spouse is streaming a movie. 
Otherwise, you will want a router of your very own to mess up. 

Consider ordering one soon. I use a RouterBoard / Mikrotik "hAP lite" which I highly recommend.
I found mine on Amazon for less than $30 USD. Buy some CAT-5 cables, too.

For test computers, I use an old HP laptop that once ran Windows Vista, and a Raspberry Pi. 
Also running on the same net, I have two development Ubuntu laptops, a Windows 10 laptop, 
an old MacBook, and my Android phone. Those make a good test bed.



v v v v v v v v v v Text below should be moved to individual class lessons v v v v


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
Name your bevy: {'bevy01'}: bevy2  # type the same bevy number you selected above

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
