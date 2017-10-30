## Basics of Vagrant

[Vagrant](https://www.vagrantup.com/) is a tool to create and control Virtual Machine
environments simply. It does not run the virtual machine -- that is done by a 
[VM provider]() such as VirtualBox, Hyper-V, VMware, or Docker. 
Vagrant does the fiddly work of connecting network interfaces, shared
virtual disks, and provisioning scripts. Your configuration details are specified
in a [Ruby language](https://www.ruby-lang.org/en/) file, always named "Vagrantfile".

There might be several `Vagrantfile` instances an a project, and more than one
may be consulted in building a virtual machine. We will concern ourselves with
only one. It will be in our directory, or a parent of it.  It will define two
essential things: the name of our machine, and where to find its bootable image.
Vagrant bootable images are packaged in a "box". 
[Vagrant boxes](https://www.vagrantup.com/docs/boxes.html) may be created
by your company (or yourself, but they are not trivial to make) or downloaded from
a [public repository](https://app.vagrantup.com/boxes/search).  Each box may be
built for one or more of the possible VM providers.

Lessons here will use either [VirtualBox](https://www.virtualbox.org/) (the default)
or [VMware](https://www.vmware.com/) to run the VMs. If you wish to use VMware,
you will need to buy a commercial [VMware provider](https://www.vagrantup.com/docs/vmware/)
for your workstation. If you use only VirtualBox VMs there is nothing to buy.



#### Vagrant VMs on your workstation

A Vagrantfile is supplied here to create virtual machines on your workstation.
You can use such a VM to run the Salt Master for your "bevy", or to run one or more
application servers which you may wish to monitor or debug, or both.

You can create a Salt cloud master ("bevymaster") as a virtual machine on your workstation.
This can be very conventient, except for one restriction: your application servers 
(salt minions) will be trying to connect to their master at a fixed address. You will
need to consistently use the same network connection for your host workstation so that
 our minions can find you, or use some sort of dynamic DNS arrangement.

The Vagrantfile also defines simple empty Ubuntu 16.04 VMs suitable for management 
by Salt scripts on the bevy master. There are two, named "quail1" and "quail16".
  
There is also an Ubuntu 14.04 VM (named "quail14") defined in the Vagrantfile. 

Each of these has a pre-defined IP address range for a Vagrant host-only network adapter used
to connect a virtual directory, as the address Salt-cloud uses to ssh connect to the machines,
and for NAT networking from the VM to the world.  There is also a hard-wired address for a
[private network](https://www.vagrantup.com/docs/networking/private_network.html) which can
be used for intercommunication between the host and its virtual machines (and the VMs to each other.)
There is also a [bridged network](https://www.vagrantup.com/docs/networking/public_network.html) which
makes the VM appear to be on the same LAN segment as its host. 

If you wish to add local VMs other than these three, you will need to edit the Vagrantfile.
