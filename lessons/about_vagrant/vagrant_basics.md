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



