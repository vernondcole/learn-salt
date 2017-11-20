## This is a stub entry.


PXE boot ...

[Dragon](https://blogging.dragon.org.uk/howto-setup-a-pxe-server-with-dnsmasq/)

This one shares with an existing DHCP server. 
[Manski](https://manski.net/2016/09/pxe-server-on-existing-network-dhcp-proxy-on-ubuntu/)

About UEFI clients ...

[The Urban Penguin](https://www.theurbanpenguin.com/pxe-install-ubuntu-16-04/) has an excellent lesson.

[serverfault](https://serverfault.com/questions/829068/trouble-with-dnsmasq-dhcp-proxy-pxe-for-uefi-clients)

[orumin gist](https://gist.github.com/orumin/b38f5aed762f0bedff68)

[UBUNTU wike with UEFI](https://wiki.ubuntu.com/UEFI/PXE-netboot-install)

[serverfault](https://serverfault.com/questions/829068/trouble-with-dnsmasq-dhcp-proxy-pxe-for-uefi-clients)

[The Ubuntu 16.04 official netboot doc](https://help.ubuntu.com/16.04/installation-guide/amd64/ch04s05.html)
says "For PXE booting, everything you should need is set up in the netboot/netboot.tar.gz tarball. Simply extract this tarball into the tftpd boot image directory. Make sure your dhcp server is configured to pass pxelinux.0 to tftpd as the filename to boot. "

For Ubuntu 16.04, this is found at http://archive.ubuntu.com/ubuntu/dists/xenial/main/installer-amd64/current/images/netboot/netboot.tar.gz

