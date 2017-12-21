### Unique Local IPV6 addresses

In the IPv4 network address scheme, there are three groups of
addresses reserved for private allocation. Addresses from these
are used, by both large companies and private homes,
to generate internal IP addresses.  
For example, most home routers will use network 192.168.0.0/24,
so there are thousands of routers addressed at 192.168.0.1.

Suppose I own a small business, with Internet feeds at an office
and a shop. If I set up a network bridge so that the shop can
access the office file server, addresses on the two networks will collide.
My network guy will have to change the addresses of every machine
on one of the two networks. 

This is not a big problem for a small installation, but what happens
when a large company, with thousands of computers on their 10.0.0.0/8
network merges with another large company also using 10.0.0.0/8?

To prevent that trouble, IPv6 has set aside space for a trillion different 
private networks, and specified that your choice among the trillion chances
must be randomly determined. The RFC states: 
"They MUST NOT be assigned sequentially or with well-known numbers."
Within that network, you can have 65,565 subnets with 18,446,744,073,709,551,616
addresses on each. They assume that will be enough.

They suggest an algorithm for generating network numbers so that: 
"The local assignments are self-generated and do not need any central
coordination or assignment, but have an extremely high probability of
being unique."  
All IPv6 networks allocated using this scheme will start with the prefix "FD".

For your convenience, there is a Python program to generate such a
network number based on [RFC-4193](https://tools.ietf.org/html/rfc4193)
here in this lesson. See [rfc4193.py](./rfc4193.py).

