### Chose your cloud provider.


### Installation

Clone [1] [this git repository](https://github.com/vernondcole/learn-salt) onto your target environment --


Place it in the `/projects/learn-salt` directory[2]. Or not -- you don't really have to put it there. All lessons should work if you put it somewhere else, like `/home/myusername/learn` or wherever. 
Examples will be configured and tested to operate from any random directory you like.  
But, for simplicity sake, all examples will be given as if they were in `/projects/learn-salt`.

```bash
mkdir /projects
cd /projects
git clone https://github.com/vernondcole/learn-salt.git
cd learn-salt/configure_machine
apt install python3-pip
pip3 install pyyaml
./bootstrap_bevy_member_here.py
```


Proceed with the instructions in [the installation lesson](lessons/installation/install.md).

[1]: see [how to git stuff](lessons/git/how_to_git_stuff.md) if you don't understand what "clone" means.

### Steps to use a cloud machine as your bevy master.
 
Define a small virtual machine (1 CPU, 1GB RAM) on your cloud provider of choice.

Log in to your Bevy-Master-to-be using the user name you chose.  Mine is "vernon". 

Then download the bevy master repository.  For move explanation of the steps, refer to the "external VM" section below.

```(bash)
ssh-add -K  # Mac only -- starts authentication agent
ssh -A vernon@d-gp2-bevy2-1.imovetv.com`  # -A means "forward my agent authentication"
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

### Steps to use an external VM

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
```

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
    git clone https://github.com/vernondcole/learn-salt.git
    cd learn-salt
    ```

- run scripts to install all the files and directories.

    ```
    (bash)
    # assuming you are in the /projects/learn-salt directory...
    cd configure_member
    sudo ./bootstrap_bevy_member_here.py
    ```

Be prepared to supply the username, password, and ssh public key you wish to have installed on the bevy master and on all of the bevy minions.
This should be your preferred user name.  Salt will also create the standard "vagrant" user on all minions.

If the script detects a minion connected to another Salt master 
(not localhost) it will ask to install a second minion to connect its local Salt master.
