### Making a Hardware (or cloud-hosted) Bevy Master.

So you have learned a few things using your Vagrant bevy master and it's time to
move on to bigger things -- a salt master that will
stay running 24 hours a day.

You have three options.

- Dedicate a small machine.
- Rent a cloud instance.
- Make your own cloud (virtual machine) server.

Let's discuss the pros and cons of each.

##### Dedicated small bevy master.

If you want to repurpose an old workstation, or buy a Raspberry Pi,
this might be the choice for you. I have a 15-year-old Dell workstation that
my daughter purchased at a surplus sale from her university.
It was running Windows XT poorly, but, after blowing out all the dust
that was clogging the cooling fans, it runs LUbuntu just fine. 
I used it as my home-office file server for years.

Another option is the laptop that you retired last year 
-- or the one with the broken screen.
It has advantages of small space, low power consumption, and a built-in
uninteruptible power supply.  You just need to set the BIOS so it
does not automatically go to sleep when you close the top cover.
The built-in keyboard and screen can be very convenient, if you park it 
where you can see it and type.

The ultimate low power home server has to be the Raspberry Pi.
Mine is a model 3, which has a hardware ethernet port for a reliable
connection to my router. It is powered by a car USB adapter which 
is plugged in to the lighter socket of my cheap Harbor Freight
solar controller. The 45 watt solar panel takes about three days
to charge a size 24 marine battery, which will run the Pi for about
a week. Using it makes me feel all green and fuzzy.

##### Rent a cloud instance.

Many cloud providers have a low-end virtual machine option which they
price very reasonably. I will discuss the two I use. Other recommendations
are invited and will be included for anyone who sends in a Pull Request.

The ultimate low cost vendor has to be [Scaleway](https://www.scaleway.com/).
They bill in Euros, so each month my bill is different. When my credit
card statement comes in, I see that it cost me less than four US dollars.
My €2.99 machine is a virtual 64 bit x86 with two processors and 2GB of RAM memory.
It feels a litte weird, since the machine is located in Paris, France, but has
a '.us' domain name and I pay with American Express. It has been purring
along for over a year. But I don't actually use that one for a Salt master.

My Salt master is on a virtual machine provided by [Linode](https://www.linode.com/).
I use a 'Linode 1024' instance -- 1 GB of RAM and one CPU for $5.00 a month.
It has been absolutly solid ever since I started it in late 2015. I like
Linode because my machine has a real dedicated Internet address, both IPv4 and IPv6,
and their service has been exemplary.

The biggest advantage of a cloud instance is its Internet address. It is globally
available. Your office, whether home or commercial, is probably behind a NAT router.
You cannot reach it from outside unless you get your Internet Service Provider,
or IT department, to create a reverse-NAT path for you. With the exhaustion of
IPv4 address space, that is getting more difficult to do. My Internet provider
charges more for an IP address than what I pay for my cloud machine.

##### Run you own VM Server.

If you are modelling a complex system, like to one I was faced with when this project
got its start, you will need a really capable machine to simulate many different network
nodes. A quick look at EBay reveals that you can get a used commercial-grade server for
a few hundred dollars. It makes sense to run your bevy master on the hardware operating system,
and let Salt-cloud create your virtual machines using KVM and libvirt, or (if you are lazy)
using VirtualBox and Vagrant.

#### Provisioning your dedicated Bevy Master

- Load your operating system.

Follow the usual guidelines for installation. We assume for this lesson that you have chosen
a Debian-based system, such as Raspbian or Ubuntu-server. If your server has the appropriate
hardware, you may elect to include a graphical desktop. This lesson will use command line only.
Make sure that you include an [ssh server](https://help.ubuntu.com/lts/serverguide/openssh-server.html).

- Install prerequisite utilities.
```(bash)
# (you are typing on the console of your new machine)
sudo apt update
sudo apt install git, python3, python3-pip
sudo pip3 install pyyaml
```
- Download this repository.
```(bash)
sudo mkdir /projects
whoami
<read your username here>
sudo chown <your username> /projects
cd /projects
git clone https://github.com/vernondcole/learn-salt.git
```
- Get a dedicated IP address.
  * If you are using a cloud service, they did this for you. Write down the IP address of your instance.
  * If you are running a dnsmasq or other integrated DNS and DHCP server, set it up there.
  * Using a MikroTik router use the [web interface](http://router/webfig/) 
  or []http://192.168.88.1/webfig/](http://192.168.88.1/webfig/) if your workstation refuses to find the symbolic address.
  Select IP --> DHCP Server --> [Leases tab]
  Find your client device and copy its MAC address (or find the MAC some other way) click the `-` button on that row.
  Click on the `Add New` button and plug in the IP address you want and the MAC address you have.
  Get your machine to renew its lease. (Try running `dhclient` on Linux.)
  * Using some other router, find its DHCP table and figure out how to make a reserved address.
- If you can -- set up a DNS name for your server. Use the DNS name in preference to the IP address.
- Chose a name for the bevy this master will be creating.
- Run the Python bootstrap script.
```bash
cd /projects/learn-salt/configure_machine
sudo ./bootstrap_bevy_member_here.py
```
Answer the questions - specify `y` when asked if you are making a master.

The bootstrap script will install Salt (if needed) and run a highstate. 
When the smoke clears, you should have a running bevy master server.
