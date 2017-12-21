# -*- mode: ruby -*-
# vi: set ft=ruby :
#  .  .  .  .  NOTE  .  .  .  .
# This configuration file is written in Ruby.
# I invested one entire day in learning Ruby,
# so if this is not particularly good Ruby code, I'm sorry.
# -- vernondcole 2017 .  .  .  .
require "etc"
require "yaml"
require "ipaddr"
#
# . v . v . enter your customized values below . v . v . v . v . v . v .
# .
BEVY = "bevy01"  # change this to avoid domain name and MAC address conflicts
NETWORK = "172.17"  # the first two bytes of your host-only network IP ("192.168")
# ^ ^ your VM host will be NETWORK.2.1, the others as set below.
# ^ ^ also each VM below will have a NAT network in NETWORK.17.x/27.
DOMAIN = BEVY + ".test"  # .test is an ICANN reserved private top-level domain
bevy_mac = (BEVY.to_i(36) % 0x1000000).to_s(16)  # a MAC address based on hash of BEVY
# in Python that would be: bevy_mac = format(int(BEVY, base=36) % 0x1000000, 'x')
#
INTERFACE_GUESS = ''  # enter the Windows description for your IP interface if needed
BRIDGED_NETWORK_MASK = '192.168.88.0/24' # (if blank will try automatic) often "192.168.0.0/16"
# .
BEVYMASTER = "bevymaster." + DOMAIN  # the name for your bevy master
# .
VAGRANT_HOST_NAME = Socket.gethostname
login = Etc.getlogin    # get your own user information to use in the VM
my_linux_user = login  # username used for login to VM
HASHFILE_NAME = 'bevy_linux_password.hash'  # filename for your Linux password hash
hash_path = File.join(Dir.home, '.ssh', HASHFILE_NAME)  # where you store it ^ ^ ^
# .
ANTECEDENT_FILE_NAME = 'bevy_srv/pillar/01_bootstrap_settings.sls'
# . ^ . ^ . end of customize things . ^ . ^ . ^ . ^ . ^ . ^ . ^ . ^ . ^ .
# . . . try to get previously stored settings values to replace above . . .
if File.exists?(ANTECEDENT_FILE_NAME)
  settings = YAML.load_file(ANTECEDENT_FILE_NAME)
  my_linux_user = settings['my_linux_user']
else
  settings = nil
  if ARGV[0] == "up"
    puts "Unable to read settings file #{ANTECEDENT_FILE_NAME}. Using defaults."
    end
end
# . v . v . the program starts here . v . v . v . v . v . v . v . v . v .
#
vagrant_command = ARGV[0]

# Ubuntu uses weird network adapter names, so we may need to scan for them.
def get_good_ifc()   # try to find a working Ubuntu network adapter name
  addr_infos = Socket.getifaddrs
  addr_infos.each do |info|
    a = info.addr
    if a and a.ip? and a.ipv4? and not a.ipv4_loopback? and not a.ip_address.start_with?(NETWORK)
      # this may be a good name.
      addy = a.ip_address.split('.')
      if BRIDGED_NETWORK_MASK.empty?
        if addy[0] == "10"  # make a netmask for the 10 net
          network_mask = "10.0.0.0/8"
        else  # make a generic netmask.  Will not be perfect, might work.
          addy[2] = "0"
          addy[3] = "0"
          network_mask = addy.join(".") + "/16"
        end
        puts "Making a generic network mask: #{network_mask} for #{info.name}"
        return info.name, network_mask
      else
        nmsk = IPAddr.new(BRIDGED_NETWORK_MASK)
        if nmsk.include?(a.ip_address)
          puts "Found interface= #{info.name} using #{a.ip_address} in #{BRIDGED_NETWORK_MASK}"
          return info.name, BRIDGED_NETWORK_MASK
        end
      end
    end
  end
  puts "Unable to find a network interface in #{BRIDGED_NETWORK_MASK}. Using default."
  return "eth0", BRIDGED_NETWORK_MASK   # nothing found. fall back to default
end

# Bridged networks make the machine appear as another physical device on your network.
# We must supply a list of names to avoid Vagrant asking for interactive input
#
network_mask = BRIDGED_NETWORK_MASK
if (RUBY_PLATFORM=~/linux/)  # on Linux, scan for the device name
  ifc_name, network_mask = get_good_ifc()
  interface_guesses = [ifc_name]
elseif (RUBY_PLATFORM=~/darwin/i)  # on Mac OS, guess two frequently used ports
  interface_guesses = ['en0: Ethernet', 'en1: Wi-Fi (AirPort)']
else  # on Windows -- you really have to type in a value, they are too weird.
  interface_guesses = [INTERFACE_GUESS]
end
if ARGV[0] == "up" or ARGV[0] == "reload"
puts "Running on host #{VAGRANT_HOST_NAME}"
puts "Will try bridge network using interfaces: #{interface_guesses}"
end

Vagrant.configure(2) do |config|  # the literal "2" is required.
  info = Etc.getpwnam(login)

  config.ssh.forward_agent = true

  config.vm.provision "shell", inline: "ip address", run: "always"  # what did we get?


  # . . . . . . . . . . . . Define machine QUAIL1 . . . . . . . . . . . . . .
  config.vm.define "quail1", primary: true do |quail_config|  # this will be the default machine
    quail_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail1." + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.8"  # needed so saltify_profiles.conf can find this unit
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|  # only for VirtualBox boxes
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.0/27"]  # do not use 10.0 network for NAT
	end  #                                                     ^  ^/27 is the smallest network allowed.
    quail_config.vm.provider "vmware" do |v|  # only for VMware boxes
        v.memory = 1024       # limit memory for the vmware box, too
        v.cpus = 1
		v.linked_clone = true
	end
  end


  # . . . . . . .  Define the BEVYMASTER . . . . . . . . . . . . . . . .
  config.vm.define "bevymaster", autostart: false do |master_config|
    master_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    master_config.vm.hostname = BEVYMASTER
    master_config.vm.network "private_network", ip: NETWORK + ".2.2"  # your host machine will be at NETWORK.2.1
    master_config.vm.network "public_network", bridge: interface_guesses, mac: "be0000" + bevy_mac
    master_config.vm.synced_folder ".", "/vagrant", :owner => "vagrant", :group => "staff", :mount_options => ["umask=0002"]

    if vagrant_command == "ssh"
      master_config.ssh.username = my_linux_user  # if you type "vagrant ssh", use this username
      master_config.ssh.private_key_path = info.dir + "/.ssh/id_rsa"
    end

    master_config.vm.provider "virtualbox" do |v|
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.32/27"]  # do not use 10.0 network for NAT
    end

    master_config.vm.provider "vmware" do |v|
        v.memory = 1024       # limit memory for the vmware box, too
        v.cpus = 1
		v.linked_clone = true
	end

    script = "mkdir -p /srv/pillar\n"  # put a skeleton /srv on the new master
    script += "test -e /srv/pillar/my_user_settings.sls || echo '# placeholder file created by Vagrant provision' > /srv/pillar/my_user_settings.sls\n"
    script += "mkdir -p /srv/salt/ssh_keys\n"
    script += "chown -R vagrant:staff /srv/salt\n"
    script += "chmod -R 775 /srv/salt\n"
    master_config.vm.provision "shell", inline: script

    master_config.vm.provision :salt do |salt|
       # # #  --- error in salt bootstrap when using git 11/1/17
       salt.install_type = "git 9865a31e62dcf6b7d6184777483685e4f054168b"  # TODO: use "stable" when OXYGEN is released
       # # #  ---
       salt.verbose = true
       salt.colorize = true
       salt.bootstrap_options = "-P -M -L -g https://github.com/vernondcole/salt.git"
       # TODO: salt.bootstrap_options = ''-P -M -L -c /tmp'  # install salt-cloud and salt-master
       salt.masterless = true  # the provisioning script for the master is masterless
       salt.run_highstate = true
       salt.minion_config = "configure_machine/minion"
       password_hash = ''
       if File.exists?(hash_path)
         File.foreach(hash_path, 'r') do |hashline|
           hashline.strip!
           if hashline.length > 0
             password_hash += hashline
           end
         end
       else
         puts "NOTE: file #{hash_path} not found. No linux password will be supplied."
       end
       if settings
         uid = settings['my_linux_uid']
         gid = settings['my_linux_gid']
       elsif info  # info is Null on Windows boxes
         uid = info.uid
         gid = info.gid
       else
         uid = ''
         gid = ''
       end
       salt.pillar({ # configure a new interactive user on the new VM
         "my_linux_user" => my_linux_user,
         "my_linux_uid" => uid,
         "my_linux_gid" => gid,
         "bevy_root" => "/vagrant/bevy_srv",
         "bevy" => BEVY,
         "node_name" => "bevymaster",
         "bevymaster_address" => NETWORK + '.2.2',
         "run_second_minion" => false,
         "linux_password_hash" => password_hash,
         "force_linux_user_password" => true,
         "vagranthost" => VAGRANT_HOST_NAME,
         "network_mask" => network_mask,
         "runas" => login,
         "cwd" => Dir.pwd,
         "doing_bootstrap" => true,  # flag for Salt state system
                   }
         )
       end
  end


  # . . . . . . . . . . . . Define machine QUAIL16 . . . . . . . . . . . . . . 
  config.vm.define "quail16", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail16." + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.3"  # needed so saltify_profiles.conf can find this unit
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.64/27"]  # do not use 10.0 network for NAT
	end
    quail_config.vm.provider "vmware" do |v|
        v.memory = 1024       # limit memory for the vmware box, too
        v.cpus = 1
		v.linked_clone = true
	end
  end


 # . . . . . . . . . . . . Define machine QUAIL14 . . . . . . . . . . . . . . 
  config.vm.define "quail14", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/trusty64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail14." + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.4"  # needed so saltify_profiles.conf can find this unit
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.96/27"]  # do not use 10.0 network for NAT
	end
    quail_config.vm.provider "vmware" do |v|
        v.memory = 1024       # limit memory for the vmware box, too
        v.cpus = 1
		v.linked_clone = true
	end
  end


# . . . . . . .  Define Quail42 as the answer to everything. . . . . . . . . . . . . .
# . this machine has Salt installed but no states run or defined.
# . Its master is "bevymaster".
  config.vm.define "quail42", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail42." + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.5"  # your host machine will be at NETWORK.2.1
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|
        v.memory = 4000       # limit memory for the virtual box
        v.cpus = 2
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.96/27"]  # do not use 10.0 network for NAT
    end

    quail_config.vm.provider "vmware" do |v|
        v.memory = 4000       # limit memory for the vmware box, too
        v.cpus = 2
        v.linked_clone = true
    end

    quail_config.vm.provision :salt do |salt|
       # # #  --- error in salt bootstrap when using git 11/1/17
       salt.install_type = "-f git" # b7c0182d93a1092b7369eedfbcf5bc2512c12f1b"  # TODO: use "stable" when OXYGEN is released
       # # #  ---
       salt.verbose = false
       salt.colorize = true
       salt.bootstrap_options = "-A " + NETWORK + ".2.2 -i quail42 -F -P " # -g https://github.com/vernondcole/salt.git"
       # TODO: salt.bootstrap_options = '-A ' + NETWORK +'.2.2 -i quail42 -P -c /tmp'  # expect Master at x.x.2.2
       salt.masterless = true  # the provisioning script is masterless
    end
  end
end
