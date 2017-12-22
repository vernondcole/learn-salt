## Vagrant Tutorial

### Lesson 1

_gentle reminder: the directory `/projects/learn-salt` here is a convention only.
you may have placed your repository elsewhere._

Run this lesson on your machine for practice, do not just read it.

The simplest `Vagrantfile` lists only the name of the virtual machine,
and the source of the bootable image. The one for this lesson is...

```Ruby
Vagrant.configure(2) do |config|
  config.vm.define "lesson1" do |quail_config|
    quail_config.vm.box = "boxesio/xenial64-standard" 
    quail_config.vm.hostname = "lesson1.test"
  end
end
```

The name of the machine will be "lesson1", and its fully qualified
domain name will be "lesson1.test".

The bootable image will be found in the public repository in a box
named "boxesio/xenial64-standard".

Before starting your first VM, click on the control to start your VirtualBox 
(or other VM provider of your option) [manager GUI](empty_VMmgr.png).
It should be empty. You will not use this to add or control machines
(unless one gets out from under Vagrant's control) but it makes a
good display of what Vagrant is doing.

#### Start your first Vagrant VM

```(bash)
cd /projects/learn-salt/lessons/vagrant_basics
ls -al
vagrant up
``` 

Vagrant will tell you that it is importing your box. Soon you will see
the machine appear in the [GUI window](running_VM.png). Note that the
machine name you supplied ("lesson1") is part of the longer ID that
VirtualBox uses. Clicking on various places on the GUI will show you
several things the Vagrant has prepared for you, including a NAT-enabled
network adapter. 

The box was defined with a user named "vagrant" who has
the password "vagrant". The scrolled output from "vagrant up" tells you
that Vagrant defined a local port (2222 probably, YMMV) which will be 
forwarded to the guest's port 22. Knowing this, we can connect to our VM.

```(bash)
ssh vagrant@127.0.0.1 -p 2222
```
Type the password "vagrant" when prompted:

Then try the commands:`hostname`, `hostname --fqdn`, and `ls -al /vagrant`.

```
$ ssh vagrant@127.0.0.1 -p 2222
vagrant@127.0.0.1's password: 
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-21-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage
vagrant@lesson1:~$ hostname
lesson1
vagrant@lesson1:~$ hostname --fqdn
lesson1.test
vagrant@lesson1:~$ ls -al /vagrant
total 264
drwxrwxr-x  1 vagrant vagrant   4096 Oct 30 21:12 .
drwxr-xr-x 23 root    root      4096 Oct 30 20:50 ..
-rw-rw-r--  1 vagrant vagrant   3162 Oct 30 20:09 basics_of_vagrant.md
-rw-rw-r--  1 vagrant vagrant 112757 Oct 30 20:43 empty_VMmgr.png
-rw-rw-r--  1 vagrant vagrant 123045 Oct 30 20:54 running_VM.png
-rw-rw-r--  1 vagrant vagrant   2242 Oct 30 21:12 tutorial.md
drwxrwxr-x  1 vagrant vagrant   4096 Oct 30 20:11 .vagrant
-rw-rw-r--  1 vagrant vagrant    258 Oct 30 20:12 Vagrantfile
vagrant@lesson1:~$ 
```

The contents of the `/vagrant` directory should look familiar to you.
It is the same directory as `/projects/learn-salt/lessons/vagrant_basics`.
It is not a *copy* of that directory, it is the *same* directory.
Any changes made by one machine are immediatly seen by the other.

This means that you can take full advantage of the high-end IDE
(such as [PyCharm](https://www.jetbrains.com/pycharm/)), running on
your workstation, to maintain code your VM. The professional version
can do line-by-line interactive debugging of a program running on the VM.

Feel free to play around with the VM as much as you wish. We will throw it
away in a few moments.

When you are done, log off the VM using the Lunix `exit` command.  Your terminal
will return to controlling your workstation.

During the "vagrant up" operation, did you notice the references to "insecure key"
and "newly generated keypair"? Vagrant has prepared the guest VM for passwordless
login.  You can check the configuration by:

```bash
vagrant ssh-config
```

Vagrant will print all the details needed to connect to the VM. It can use them for you.
Just type: `vagrant ssh`

That was easy, wasn't it?

To stop your VM, you can either `sudo shutdown -h now` from within the VM, or have Vagrant
do it for you: `vagrant halt`.

Either way, reboot the VM using `vagrant up`.

To maintain the state of the VM, but keep it from using your host's CPU and memory,
use `vagrant suspend`.  Wake it up using `vagrant resume` or our old friend `vagrant up`.

Finally, to remove the VM from your machine, recovering all of the resources,
including its "box" on your hard disk storage, use the command `vagrant destroy`.

After running `vagrant destroy` you will need to download the "box" again (unless you
happened to say `linked_clone = true` in your Vagrantfile.)

### Vagrant Commands for multi-machine Vagrantfiles

A `Vagrantfile` can grow much more complex -- like the one in the top level directory
of this repository. It contains definitions for several different machines. One is
defined as the `primary` and will react the same as the `lesson1` machine here.
The others must be explicitly specified on the Vagrant command line. For example,
to start the machine named "quail16", you type `vagrant up quail16`.

### IP Networks in Vagrant

Vagrant needs to use TCP/IP networking for the host to talk to its guests.
The guest machine needs to be able to reach the Internet and corporate resources.
Guest machines will want to talk to the host, and to other guests.
Lastly, other machines on a corporate network will need access to the guest.
Vagrant uses three different virtual network adapters to meet the different needs.

The default adapter has a [NAT](https://en.wikipedia.org/wiki/Network_address_translation) setup,
and uses the host's interface, and its address, to connect to Internet resources. 
Because of NAT, guest packets appear to originate from the host.  
This adapter is also used for ssh connections from the host when you use `vagrant ssh`.
Vagrant uses a different small [private network](https://en.wikipedia.org/wiki/Private_network) for each guest.

The second adapter is for what Vagrant calls a 'host only' network. 
The host computer acts as a router for traffic among guest machines and itself.
This network must have a unique (among your route) [private network](https://en.wikipedia.org/wiki/Private_network) number.

The third adapter is for a [bridged network](https://en.wikipedia.org/wiki/Bridging_(networking)).
Using a combination of smoke, mirrors, and magical incantations, this virtual interface
makes the network think that your host's physical network adapter is suddenly two adapters.
The virtual adapter has its own [MAC address](https://en.wikipedia.org/wiki/MAC_address)
and, therefore, it gets a unique [IP address](https://en.wikipedia.org/wiki/IP_address).

Due to a nefarious twist in the magic, it often happens that bridged packets cannot travel 
between the physical adapter and its virtual adapters. 
Therefore you must use the 'host only' network to talk between the host and amoung guests.

For some odd reason, VirtualBox uses the descriptive network name, 
rather than the adapter name shown by `ifconfig` (`ipconfig` on Windows),
to describe which network adapter should be used for the bridge interface.
That name is not easy to determine.

The [supplied Vagrantfile](../../Vagrantfile) contains a rather large section of code to try finding the 
correct name for the bridge interface.
On Linux, it will probe all of the interface addresses to find one within `BRIDGED_NETWORK_MASK`.
On MacOS, it will try two frequently found Mac interfaces.
On Windows -- you are out of luck.
What you need to do is to use `vboxmanage list bridgedifs` to list the possible bridge interface names.
Then copy the name you found into the constant `INTERFACE_GUESS` list.
Entries in the `INTERFACE_GUESS` list will be used in leu of probing on all operating systems.

