## How to prepare a PXE boot server.

PXE is an acronym for [Preboot Execution Environment](https://en.wikipedia.org/wiki/Preboot_Execution_Environment),
a facility for controlling the bootstrapping of a machine using the network.

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

#### Installation and use

Setup pillar/bevy_settings.sls as documented above.

```(bash)
# on the intended PXE host computer
sudo salt-call state.apply dnsmasq.pxe_ubuntu_image
```

You can see the progress of your tftp server by

`sudo tail -f /var/log/syslog`



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


