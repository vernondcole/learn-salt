## How to Prepare and Run a PXE boot server.

PXE is an acronym for [Preboot Execution Environment](https://en.wikipedia.org/wiki/Preboot_Execution_Environment),
a facility for controlling the bootstrapping of a machine using the network.

##### What this lesson covers

Using a test client workstation and a private network router, running bevy_master on a Vagrant VM,
- remote start a powered-down client computer
- automatically load an operating system image onto it
- keep it from looping the install process
- run a command to automatically join it to the bevy

When your network and configuration files are completely set up, 
you will be able to bring up a new bevy master, load a new target OS, and connect your
client hardware machine, in three lines:

```bash
vagrant up bevymaster
vagrant ssh bevymaster
sudo salt-call state.apply bevy_master.test.full_rebuild_saltify_machine
```
##### Caution: only one...
There can only be one server for extended DHCP requests on any network segment.

If someone else (your IT department) is running a PXE server, 
they will not appreciate competition. 
Also do not compete with yourself -- like running both a hardware and virtual PXE machine. 
 
#### The Boot Server and Process

Our setup here will use [dnsmasq](http://thekelleys.org.uk/dnsmasq/doc.html),
a lightweight server which combines servers for DNS, DHCP, and TFTP, all
of which are needed for PXE booting to work. But, in most environments there is
already a working DHCP server which hands out network addresses, so the example here
will use dnsmasq in a proxy role to only supply the additional DHCP functions
of the PXE process. 

Use of dnsmasq as a real DNS and DHCP server will be discussed elsewhere.

The PXE boot process is designed to display a menu of boot choices, similar to the
menu provided by `grub` when booting from a hard drive.  If there is only one choice
on the menu, that choice is run immediatly. We will take advantage of that short-cut by
always supplying only one choice.

The example files are set to operate on a small network at IP address 192.168.88.0/24. 
A test network for this setup has been provided by an inexpensive MikroTik "hAP lite" router.
Almost any home router could probably be used, but the MikroTik operating software provides more
functionality for an experienced network technician. The router provides basic DHCP service, 
including the possibility of reserving fixed addresses for the host, bevy master, and test bed computers.

The examples can also be run on a larger net by appropriate juggling of the IP addresses, provided that the
large net does not have extended PXE support already in place. If more that one "bevy" of test systems is
present on a local network it is important that they use different BEVY identification strings to avoid
conflict.

#### Wake-On-Lan

SaltStack has [integrated support](https://docs.saltstack.com/en/latest/ref/modules/all/salt.modules.network.html#salt.modules.network.wol) 
for [Wake-on-LAN](https://en.wikipedia.org/wiki/Wake-on-LAN)
which has been extended to [work with salt-cloud](https://docs.saltstack.com/en/latest/topics/cloud/saltify.html#getting-started-with-saltify)
starting with the [Salt Oxygen version](https://docs.saltstack.com/en/latest/topics/releases/version_numbers.html).

The example files bevy_srv/pillar/bevy_settings.sls and 
/etc/salt/cloud.profiles.d/saltify_demo_profiles.conf
contain code to wake a hardware machine. Note especially that the machine which sends
the Wake-on-LAN `magic packet` (identified by the pillar variable `wol_test_sender_id`) must be on the same network segment 
as the machine to be awakened. (Exception: routers can be set up to forward WOL magic packets.)

Combining Wake-on-LAN with PXE installation makes it possible for turn on a suitably configured powered-down
machine and build a new bootable image on it, or run it as as diskless server.

Prepare your WoL client. For security reasons, the Wake-on-LAN facility on most computers is disabled by default.
Using the BIOS setup for your target machine, hunt around for the appropriate setting
and enable it. It will usually be found in the built-in device area, not with the boot options.

Get the ethernet MAC address of your client computer. If it is already running an operating system,
you can ask it. On Linux (or similar) type `ifconfig`, locate your wire ethernet adapter (often `eth0`)
and find a line like `ether 00:50:b6:5a:6d:3f`. That is the MAC address. 
On Windows, the command is `ipconfig /all`.  Otherwise, try looking on your DHCP server (on your router?)
or attempt a network boot and find it on the console screen. 
The format for displaying MAC addresses is not standardized. Hex digit pairs might be separated by ":" or "-"
or spaces, or run together. The salt `network.wol` command will accept any such format.

Test your WoL using the Salt execution module. Select a sending computer. It must have a salt minion installed and be on
the same network segment as the client. Let's say your client's MAC address was 00-1a-4b-7c-2a-b2.

```(bash)
# on the sending computer...
sudo salt-call network.wol 00-1a-4b-7c-2a-b2 --local
```

If your sending computer's Salt node name were `pizero`...

```(bash)
# on the Salt master...
sudo salt pizero network.wol 00-1a-4b-7c-2a-b2
```

Edit the three `wol_test_` settings in bevy_srv/pillar/bevy_settings.sls in
order to run WoL from a salt state.

```(bash)
# on the Salt master...
sudo salt '*' saltutil.sync_all
sudo salt '*' state.apply bevy_master.test.wake_on_lan
```

#### Beginning PXE Boot

Each ethernet device, when it is manufactured, is given a number, called a MAC address,
which is theorecically unique. The MAC address is used for all communication over the local
network -- the group of computers which can "hear" each other.  In order to talk to distant
computers, it must have an IP (Internet Protocol) address.

Normally, when a computer is bootstrapped, one of the first things it does is ask a neighbor to tell
it what its IP address should be. A nearby computer, the DHCP server, will issue an address, and
tell the new machine what that address is, along with other basic network information.

The DHCP protocol also allows for more extensive information to be passed -- such as where to
find bootstrap information. This extended DHCP data can be sent by a different server than the
one which issued the IP address. Since most computers have no need of the extra information --
they already know how to boot themselves -- most networks have only a basic DHCP service.

This subsystem is a set of Salt states to deploy an extended DHCP server to provide bootstrap information,
but allow the standard DHCP server to work as usual. Since all configuration must be based on the only fact
the server knows about the requesting unit -- its MAC address -- the setup of the boot server is manual and
fussy.

If the PXE boot configuration is set for installing a new operating system, it can also include a reference to 
a "preseed" file which contains answers to the questions which must otherwise be answered by the human operator. 
The example given here defines a default user which Salt will use to complete the configuration of the machine,
and the installation of an SSH server on it.

The example setup happens to use a single machine for WoL, salt/bevy master, and PXE boot server. This could be either a
Vagrant VM or a Raspberry Pi. The router is set to reserve the following addresses:
- 192.168.88.1 - router 
- 192.168.88.2 - bevymaster   (Vagrant will assign MAC address BE-00-00-22-97-E1 for "bevy01")
- 192.168.88.3 - my VM host workstation
- 192.168.88.8 - PXE test bed (a ten-year-old hp laptop)
- A MikroTek's DHCP reservation menu is at IP -> DHCP Server -> "Leases" tab, click on \[Add New\]. YMMV

#### The PXE netboot image

[The Ubuntu 16.04 official netboot doc](https://help.ubuntu.com/16.04/installation-guide/amd64/ch04s05.html)
says "For PXE booting, everything you should need is set up in the netboot/netboot.tar.gz tarball. Simply extract this tarball into the tftpd boot image directory. Make sure your dhcp server is configured to pass pxelinux.0 to tftpd as the filename to boot."

For Ubuntu 16.04, this is found [in this archive](http://archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64/current/images/netboot/netboot.tar.gz).

For other versions, try looking in [http://help.ubuntu.com](http://help.ubuntu.com)
in the "per architecture" installation guide. It seems that only LTS (long term support)
versions have complete guides, but net boot packages are available for all versions,
and are located in a similar directory tree to their LTS counterparts. Just change the
release name in your directory search, for example, substitute "artful" for "xenial"
and find a 17.10 release in [http://archive.ubuntu.com/ubuntu/dists/artful/main/installer-amd64/current/images/netboot/](http://archive.ubuntu.com/ubuntu/dists/artful/main/installer-amd64/current/images/netboot/netboot.tar.gz)

Edit your the URL for the netboot file in your `pillar/bevy_settings.sls` file setting `pxe_netboot_download_url`.
The initial unpacking of the tarball will be in your pxe server's /opt directory tree.

#### Installation and use of the PXE host

Setup pillar/bevy_settings.sls as documented above.

```(bash)
# on the intended PXE host computer
sudo salt-call state.apply dnsmasq.pxe_auto_install
```

This will define your tftp server and load all of the files it needs,
including the netboot installation kit from the Ubuntu repository.

It will also create the individual configuration files for each machine
defined in your bevy_settings pillar file. To queue your machines for automatic
installation again, re-apply the `dnsmasq.pxe_auto_install` state.

Review what is going on using `tree /srv/tftpboot`

You can see the operation of your tftp server by
`sudo tail -f /var/log/syslog`.

You start the installation process by turning the client computer on.
You can run a sample script using WoL to kick things off:
`sudo salt-call state.apply bevy_master.test.full_rebuild_saltify_machine`

##### DO NOT PANIC

When the auto install process completes correctly, your target machine may show
nothing but a black screen. It will not respond to the keyboard. 
This is the expected behavior. 

Just hit `<ctrl><alt><F1>` and you will get a login prompt. 
You can also use `<F2>` through `<F6>` to get additional terminals. 
`<ctrl><alt><F7>` is a log of your post-bootstrap operation.

##### The PXE_Clearing_Daeman

If the files on the tftp server were left unchanged, your client machine would
be stuck in a loop, rebooting and reloading the OS forever. In order to break
the loop, we need a little help.

When you run the `dnsmasq.pxe_auto_install` script, it creates and runs a lightweight
HTTP server on TCP port 4545. You can re-run the script at 
`/srv/tftpboot/preseed/file_clearing_daemon.py`.
It asks Salt for the pillar information from bevy_settings.sls for its control.
It will accept HTML requests and execute them as Linux commands, giving you 
(and everyone else)
complete power to start jobs on the PXE server machine. 

Because it is a glaring security hole we don't  want to leave it running. It will time
out on its own, but shuts down quickly when it thinks its work is done. The pxe_auto_install 
state sends it a 'store' request for each machine. When it has received an 'execute'
request from each one, it turns itself off. You can also turn it off with a 'shutdown' request.

The query option `pxe_config_file` must contain the name of your boot configuration file.
The daemon will replace the contents of that file with a script (stored within its own
Python code) to tell your target computer to boot from its first hard drive henceforth.

The query option `next_command` will execute the text from that command (as ROOT) on the
tftp server computer. The idea is to run a command to provision the new system.
The example script runs a `salt-cloud` command to force a Salt minion onto it, and
connect it to the bevy_master.

`pxe_config_file` and `next_command` options can be send with the `execute` query, or
stored by the `store` query. `store`d commands will be run when the `execute` query runs.
 

#### Controlling what happens during and after OS installation on each machine.

The control is tucked into a small place in `pillar/bevy_settings.sls`.

```
# This is a list of dicts of machines to be PXE booted.
#  each should have a "tag" matching the Netboot Tags below.
#  Salt state file dnsmasq/pxe_auto_install.sls will create a PXE configuretion setting file for each entry in this list.
pxe_netboot_configs:
  - mac: '00-1a-4b-7c-2a-b2'  {# Note the "-" -- this line starts a list #}
    subdir: '{{ default_ubuntu_version }}/'  # include a trailing "/"
    tag: install
    kernel: ubuntu-installer/amd64/linux
    append: 'vga=788 initrd=ubuntu-installer/amd64/initrd.gz auto-install/enable=true preseed/url=tftp://{{ pxe_server_ip }}/preseed.files/'
    next_command: 'sleep 60;salt-cloud -p hw_demo x_hw'  {# pxe_clearing_deamon will send this command when install completes #}
```
Lets discuss what each line does...
- mac: The only way the PXE server can tell machines apart is by their MAC address.
It must serve as the key for everything else.
- subdir: Each installation kit found is in a different subdirectory of the tftp server.
- tag:  Tells dnsmasq which boot control your machine should use. Defaults to running a memory test.
- kernel:  Identifies what file on the tftp server to boot.
- append:  The last part of the boot command line. This is where we can tell the new kernel
what we want it to do, including where to find its auto-install commands.
- next_command: The command line for pxe_clearing_daemon to execute on the server at the end of the client's installation
process, just before the client reboots (hopefully into its new operating system).

#### For more information...

PXE boot references ...

To see a list of PXE option numbers, log in to a machine with dnsmasq installed, and type
`dnsmasq --help dhcp` or `dnsmasq --help dhcp6`. Note that options numbers for IPv6 are different
from the same option in IPv4.

[PXELINUX documentation](http://www.syslinux.org/wiki/index.php?title=PXELINUX) is authoritative on boot configuration.

[UbuntuHowTo](https://help.ubuntu.com/community/DisklessUbuntuHowto) Diskless workstation operation on Ubuntu.

[dnsmasq man page](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html) Official from the guy who wrote dnsmasq.

[Dragon](https://blogging.dragon.org.uk/howto-setup-a-pxe-server-with-dnsmasq/) a blog post on pxe with dnsmasq.

[Manski](https://manski.net/2016/09/pxe-server-on-existing-network-dhcp-proxy-on-ubuntu/)
This blog example coexists with an existing DHCP server -- our setup is taken from this.

About UEFI clients ...

[The Urban Penguin](https://www.theurbanpenguin.com/pxe-install-ubuntu-16-04/) has an excellent lesson.

[serverfault](https://serverfault.com/questions/829068/trouble-with-dnsmasq-dhcp-proxy-pxe-for-uefi-clients) talking about solving a problem.

[orumin gist](https://gist.github.com/orumin/b38f5aed762f0bedff68) A sample installation.

[UBUNTU wiki with UEFI](https://wiki.ubuntu.com/UEFI/PXE-netboot-install) Specific Ubuntu considerations. 

About preseed files...

[Ubuntu help for installation](https://help.ubuntu.com/lts/installation-guide/armhf/apbs02.html) preseeding page

["Hands-off" Debian](http://hands.com/d-i/) from the package author (with debugging hints).


