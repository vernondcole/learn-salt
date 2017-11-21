## How to prepare a PXE boot server.

[The Ubuntu 16.04 official netboot doc](https://help.ubuntu.com/16.04/installation-guide/amd64/ch04s05.html)
says "For PXE booting, everything you should need is set up in the netboot/netboot.tar.gz tarball. Simply extract this tarball into the tftpd boot image directory. Make sure your dhcp server is configured to pass pxelinux.0 to tftpd as the filename to boot. "

For Ubuntu 16.04, this is found [in this archive](http://archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64/current/images/netboot/netboot.tar.gz).

For other versions, try looking in [http://help.ubuntu.com](http://help.ubuntu.com)
in the "per architecture" installation guide. It seems that only LTS (long term support)
versions have complete guides, but net boot packages are available for all versions,
and are located in a similar directory tree to their LTS counterparts. Just change the
release name in your directory search, for example, substitute "artful" for "xenial"
and find a 17.10 release in [http://archive.ubuntu.com/ubuntu/dists/artful/main/installer-amd64/current/images/netboot/](http://archive.ubuntu.com/ubuntu/dists/artful/main/installer-amd64/current/images/netboot/)


To see a list of PXE option numbers, log in to a machine with dnsmasq installed, and type
`dnsmasq --help dhcp` or `dnsmasq --help dhcp6`. Note that options numbers for IPv6 are different
from the same option in IPv4.



PXE boot references ...

[PXELINUX documentation](http://www.syslinux.org/wiki/index.php?title=PXELINUX) is very authoritative.

[Dragon](https://blogging.dragon.org.uk/howto-setup-a-pxe-server-with-dnsmasq/)

This one shares with an existing DHCP server. 
[Manski](https://manski.net/2016/09/pxe-server-on-existing-network-dhcp-proxy-on-ubuntu/)

About UEFI clients ...

[The Urban Penguin](https://www.theurbanpenguin.com/pxe-install-ubuntu-16-04/) has an excellent lesson.

[serverfault](https://serverfault.com/questions/829068/trouble-with-dnsmasq-dhcp-proxy-pxe-for-uefi-clients)

[orumin gist](https://gist.github.com/orumin/b38f5aed762f0bedff68)

[UBUNTU wike with UEFI](https://wiki.ubuntu.com/UEFI/PXE-netboot-install)

[serverfault](https://serverfault.com/questions/829068/trouble-with-dnsmasq-dhcp-proxy-pxe-for-uefi-clients)

