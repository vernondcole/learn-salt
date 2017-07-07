# Salt Master / Cloud Project (Configure_master subdirectory)

This sub-directory provides a manually configured SaltStack master server with integrated salt-cloud.

### How to install a cloud master manually.

- Log in to your proposed Salt Master. We presume you are using ssh for this.  The name you logged with will
be referred to below as "<ssh user>".

- Decide on your project root directory.  I find it very convenient to create:

    ```(bash)
    sudo mkdir /projects
    sudo chown <ssh user>:staff /projects
    ```

- Clone this repo onto your prospective bevy master using git.

    ```(bash)
    sudo apt install git  # if needed...
    cd /projects  # go to your project directory
    git clone ssh://git@p-bitbucket.imovetv.com/msl/bevymaster.git
    cd bevymaster
    ```

- Create a directory for your personalizations.  When the bevy master is created automitcally, Vagrant creates
 a Vagrant share with this name. Lacking that, we need to provide the same information to our new bevy master.

    ```(bash)
    sudo mkdir /my_home
    sudo chown <ssh user> /my_home
    ```

- Send all of your ssh certificates to the new machine.  __Pay attention!__: _the next set of commands is typed on 
another terminal window back on your own workstation._ 

    ```(bash)
    #  [ on your personal workstation ]
    cd ~
    ssh-copy-id <ssh user>@<your new bevy master>
    scp -r .ssh <ssh user>@<your new bevy master>://my_home
    ```

    Note: for a bit more security, you may wish to delete the //my_home/.ssh directory after this process is complete. 

- Run a shell command to accomplish the bootstrap process.  
(You may need to supply your "ssh user" password if needed by sudo.)

    ```(bash)
    sh bootstrap_bevy_master_here.sh
    ```
   
#####Establish your own private nameserver (don't really need this at the present)

This will install the dnsmasq server for DNS name and DHCP service for the 192.168.16.0:24 net
(or where you set in the pillar/cloud-master.sls file). It will also set your Mac workstation to look
at that nameserver for the .local domain, and return the 'salt' dns name as the address of your resident Salt-master at 192.168.16.1.

    sh 4_setup_nameserver.sh


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


