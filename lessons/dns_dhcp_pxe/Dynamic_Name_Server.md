## This is a stub entry.

try: 

[dnsmasq man page](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html#lbAB)

[Oracle](https://docs.oracle.com/cd/E37670_01/E41137/html/ol-dnsmasq-conf.html)




#####Settings to use my own local nameserver on my Mac...

I could not find an automated way to alter the order of nameserver resolution on a Macintosh.
In order to make full use of your dnsmasq caching nameserver for inquiries by Mac-based clients, you will need to make the following change by hand
using the GUI screens. (The `.local` domain will use your dnsmasq server without this change.)


1. Choose Apple menu > System Preferences, then click Network.

2. Select the network connection service you want to use (such as Wi-Fi or Ethernet, unless you named it something else) in the list, then click Advanced.

3. Write down the IP addresses of nameservers which are already there (from DHCP).

3. Click DNS, then click Add at the bottom of the DNS Servers list. Enter your loopback IP address: `127.0.0.1` as the top entry.

4. Replace the IP addresses of your automatically supplied nameservers.

4. When you’re finished, click OK
