# Learn Salt Project (Configure_machine subdirectory)

This sub-directory provides for manually configuring a master server or a minion.

### How to create a bevy master on your workstation.

If it is running Linux, you can run a Salt Master directly on your workstation.
Windows users must run Salt Master on a virtual machine.
MacOS users may attempt to run a Salt Master, but that configuration is not supported.
Linux users will probably find it more convenient to run the master on a VM also.


- Clone this repository onto your workstation.

- Edit the `Vagrantfile` to update
  - The bevy name `BEVY = "mybevy"`
  - an unused private network prefix ``

### How to create a bevy master on an independent computer.

- Log in to your proposed Salt Master.
This must be a Linux machine. Windows will not work. MacOS might work,
but is not officially supported. [Raspbian](https://www.raspberrypi.org/downloads/raspbian/)
and [Ubuntu Server](https://www.ubuntu.com/server) are known to work.

- Decide on your project root directory.  I find it very convenient to create:

    ```(bash)
    sudo mkdir /projects
    sudo chown <ssh user>:staff /projects
    ```

- Clone this repo onto your prospective bevy master using git.

    ```(bash)
    sudo apt install git  # if needed...
    cd /projects  # go to your project directory
    git clone --depth 1 https://github.com/vernondcole/learn-salt.git
    pip install pyyaml ifaddr
    cd configure_machine
    sudo ./bootstrap_bevy_member_here.py
    ```

- Answer "yes" to "Should this machine be the master?"

If the server machine happens to be a Vagrant VM on your workstation,
the script will attempt to share your bevy_srv directory with you.
