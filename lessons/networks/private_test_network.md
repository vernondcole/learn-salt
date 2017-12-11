### How to set up a private test network

- Get a router of your very own.
The example files are set to operate on a small network at IP address 192.168.88.0/24. 
A test network for this setup has been provided by an inexpensive MikroTik "hAP lite" router.
Almost any home router could probably be used, but the MikroTik operating software provides more
functionality for an experienced network technician. The router provides basic DHCP service, 
including the possibility of reserving fixed addresses for the host, bevy master, and test bed computers.

- Locate a hard-wire feed from your host network.
In these days of wireless operation, we are often ignoring wire networks.
We really need a wire for this, so find how to plug into your local ethernet.

- Plug your private routers `Internet` or `WAN` port into your host network.

- Plug your workstation wired port into a `LAN` port of your private router.

- Configure your router.
  * open the routers [web page at 192.168.88.1](http://192.168.88.1) for a MikroTik,
  [or try 192.168.1.1](http://192.168.1.1) for most other small routers.
  * alter your private network number so that it does not match the host network.
  * reconnect to the router if you changed addresses.
  * set up your private wireless SSID to a different name from your host's.

- Plug your lab computers into the private router (or wireless connect to the new SSID).
