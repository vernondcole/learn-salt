# Salt Master / BlackKnight "Bevy" Project

/[Refer the [connecting_a_practical_repo](../connecting_a_practical_repo.md) lesson
to see what this dirctory is used for. Text similar to that below this comment might be used 
in an actual system./]

This project provides a SaltStack master server with integrated salt-cloud to build a complete Black Knight environment.

We will use the term "bevy" to specify this collection of virtual and physical computers composing our temporary complete Black Knight system.

Using [salt-cloud](https://docs.saltstack.com/en/latest/topics/cloud/index.html),
you will create, manage, and destroy virtual computers.
You will also integrate and control physical machines using the 
[Saltify](https://docs.saltstack.com/en/latest/topics/cloud/saltify.html) driver.
Each machine is automatically connected to and accepted by your salt master.

##### Preference Settings Storage Location

During your initial bevy setup, your preferences will be stored in `/srv/pillar/01_bevy_settings.sls`
**on your workstation**. 
That file is created and maintained by `bootstrap_bevy_member_here.py`.
It is read by Salt (salt-master and salt-call --local),
and by Vagrant to configure its virtual machines. 

Configuration settings for your system should be maintained by editing various `pillar` files.

If you use a Vagrant VM as your bevy master, all will be automatic. 
But if your bevy master is on a different machine (which is the usual case), 
it will use **a different instance of** `/srv/pillar/` and confusion may occur.

It may be advisable to use some method of synchronizing your `/srv/pillar` directories
to maintain sanity. A tool like the automatic deployment feature of PyCharm would work well.
Some Salt states in this system may supply initial default `pillar` files,
but should not normally change files which are already present.

Note: The Bevy Master deploys itself using Salt. 
The `/srv/salt` directory tree should only be altered by running Salt on the Master, 
not by copying or editing, since the contents of its files are filled in from templates, 
and will be overwritten whenever the bevymaster deployment states are run.

### Integration with "learn-salt"

It happened that most of the material which was originally being written for this project was:
- completly generic
- too voluminous to be housed here

... so it was moved to a [completely generic location](https://github.com/vernondcole/learn-salt) where the sheer volume of stuff would not pollute this repo.

This repo is tightly integrated with that, and they must be cloned side-by-side for everything to work correctly.

```bash
# from the present repo . . .
./clone-learn-salt.sh
```

As soon as you have cloned that repo, all of the links below should work.  Most of your questions have answers in
the [learn-salt lessons pages](../learn-salt/lessons/index.md).  The original for your working [Vagrantfile](../learn-salt/Vagrantfile)
is there, along with a large collection of [salt states](../learn-salt/bevy_srv/salt) and the [pillars](../learn-salt/bevy_srv/pillar)
to make them work. 

You will want to set up your salt configuration files so that your [file_roots](https://docs.saltstack.com/en/latest/ref/configuration/master.html#file-roots)
has a triple source: it should include your own master's working /srv/top, and your working copies of /bevy_srv/salt and /local_salt/salt.
The simplest way to maintain the configuration of your master server would be the SFTP option on your [PyCharm IDE](https://www.jetbrains.com/pycharm/)
`settings --> deployment` page.

**Using PyCharm** you can open multiple repos in the same screen. With this repo open,
you can click `File --> Open` and select your `learn-salt` project, then in the `Open Project`
dialog box, click on `Open in current window` and tick on `Add to currently open projects`.

### your workstation as a host for bevy minions

The script in `bootstrap_bevy_member_here.py` will ask whether you wish
to use your workstation as a host for Vagrant VMs. This will provide a way
for you to debug or monitor a bevy member. Vagrant will connect each VM
using a bridging network adapter, so they will each appear as a separate
machine on the company network.
 
Vagrant can use either [VirtualBox](https://www.virtualbox.org/) (the default)
or [vmware](https://www.vmware.com/) to run the VMs. 
VirtualBox VMs use only no-cost components.
If you wish to use vmware, you will need to buy both the vmware software,
and a commercial [VMware provider](https://www.vagrantup.com/docs/vmware/)
for your workstation.

There is small shell script named `vagrant` in the `bevy_master` directory which will define the
necessary environment variable to use the `..\learn-salt\Vagranfile`, then run Vagrant.
So, to execute the command "foo" for Vagrant VM "bar", you will use either...

```bash
cd /projects/black_knight
./vagrant foo bar
```
or
```bash
cd /projects/learn-salt
vagrant foo bar
```

Another way you can do this is by using the `vagrant global-status` command. 
You can execute that command from anywhere and it will provide a list of all known virtual machines with a short hash in the first column. 
To execute "foo" for one of these machines just type:

`vagrant foo <short-hash>`

Replace <short-hash> with the actual hash of the machine.

**Using PyCharm (professional edition)** click on `Tools --> Vagrant --> Up` and select the VM you wish to start.
Then click on `File --> Settings`, click on `Project Interpreter` and click the 
settings "gear" icon in the upper right. Select `Add Remote`. 
On the next dialogue box, select `Vagrant` and pick your VM. This will use the `/vagrant` directory share on 
your VM to run Python code remotely on your VM with line-by-line stepping, etc.


##### salt-cloud configuration files

The definitions for all machines to be connected to your bevy will be created in the 
/etc/salt/cloud.profiles.d/ directory. That directory is initially populated by a Salt file.recurse
 operation which will overwrite any file found in its source directory (which is
 `/bevy_srv/salt/bevy_master/cloud.profiles.d`). -

The saltify_demo_profiles.conf and vagrant_demo_profiles files contains the demo or default examples.  
To avoid having Salt overwrite your own machine definitions, you should make a new `.conf` file with a different name. 

Each profile specifies a salt-cloud driver. Drivers are defined in the /etc/salt/cloud.providers.d/
directory. It is also populated by a Salt script, so again, to make any permanent changes, 
create a new file.

### Steps to use an external VM (or a stand-alone server) as your bevy master.
 
Your proposed bevy master must be running an ssh server (unless it _is_ your workstation).
 `sudo apt install openssh-server`

Your workstation must have a registered 
[ssh public key](https://confluence.atlassian.com/bitbucketserver0413/using-ssh-keys-to-secure-git-operations-873874478.html)
 on your BlackKnight source code control system.
 
- Log in to your proposed Salt Master using ssh agent forwarding...
    ```bash
    ssh-add -K ~/.ssh/id_rsa    # needed once per reboot, only on Mac OS-x, to register your key with your agent
    ssh -A target_username@your_proposed_master
    ```

- Decide on your project root directory.  I find it very convenient to create:

    ```bash
    sudo mkdir /projects
    sudo chown <your username>:staff /projects
    ```

- Clone this repo onto your intended master using git.

    ```bash
    sudo apt install git  # if needed...
    cd /projects  # go to your project directory
    git clone ssh://git@my_code_server.tld/black_knight.git
    cd black_knight
    ./clone-learn-salt.sh 
    ./join-bevy.sh
    ```

Be prepared to supply the username, password, and ssh public key you wish to have installed on the bevy master and on all of the bevy minions.
This should be your dish user name.  Salt will also create the standard "administrator" and "atomizer" users on all minions.

If the script detects a minion connected to another Salt master 
(not localhost) it will ask whether to install a second minion to connect its local Salt master.

#### Connect other Minions

For more information, see
https://docs.saltstack.com/en/latest/topics/cloud/qs.html

#### using salt-cloud to connect an existing machine

You can ask the bevy master use the salt-cloud `saltify` driver to bootstrap a Salt minion onto your manually
controlled machine, and connect to it. 

If you load an operating system manually onto a hardware machine,
remember to specify it as an ssh server. It is convenient, at your
 option, to define the initial username as "vagrant", even though
 your machine is not virtual.

You must enter the correct ip address, username and password in a salt-cloud
profile configuration file (in /etc/salt/cloud.profiles.d/).

#### configure your workstation as a Salt minion

So that salt-cloud can create minions on your workstation using Vagrant,
your workstation must also be running a minion. Salt-cloud will instruct the 
salt-minion on your workstation to run `./vagrant up`, etc, when needed.

- on Ubuntu (or Debian)

```bash
cd /projects/black_knight
./join-bevy.sh
```

- on MacOS  (** see NOTE above **)

```bash
brew install python3
pip3 install passlib
brew install saltstack
cd /projects/black_knight  # or your path
./join-bevy.sh
```

When asked `Should this machine BE the master?`, answer "no".

Answer the other prompts as appropriate. You will have a chance to
confirm each of your important answers before they are used.

For greatest convenience, enter the same username you use on your workstation
as your username for your bevy.
