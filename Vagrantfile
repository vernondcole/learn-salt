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
# . v . v . retrieve stored bevy settings . v . v . v . v . v . v .
BEVY_SETTINGS_FILE_NAME = '/srv/pillar/01_bevy_settings.sls'
if File.exists?(BEVY_SETTINGS_FILE_NAME)
  settings = YAML.load_file(BEVY_SETTINGS_FILE_NAME)
else
  settings = {}
  if ARGV[0] == "up"
    puts "You must run 'configure_machine\bootstrap_bevy_member_here.py'"
    puts "as an Administrator before running 'vagrant up'"
    abort "Unable to read settings file #{BEVY_SETTINGS_FILE_NAME}."
    end
end

# .
BEVY = "bevy01"  # change this to avoid domain name and MAC address conflicts
NETWORK = "172.17"  # the first two bytes of your host-only network IP ("192.168")
# ^ ^ your VM host will be NETWORK.2.1, the others as set below.
# ^ ^ also each VM below will have a NAT network in NETWORK.17.x/27.
DOMAIN = BEVY + ".test"  # .test is an ICANN reserved private top-level domain
bevy_mac = (BEVY.to_i(36) % 0x1000000).to_s(16)  # a MAC address based on hash of BEVY
# in Python that would be: bevy_mac = format(int(BEVY, base=36) % 0x1000000, 'x')
#
# .
BEVYMASTER = "bevymaster." + DOMAIN  # the name for your bevy master
# .
VAGRANT_HOST_NAME = Socket.gethostname
login = Etc.getlogin    # get your own user information to use in the VM
my_linux_user = login  # username used for login to VM
my_linux_user = settings['my_linux_user']
HASHFILE_NAME = 'bevy_linux_password.hash'  # filename for your Linux password hash
hash_path = File.join(Dir.home, '.ssh', HASHFILE_NAME)  # where you store it ^ ^ ^
# .
# . ^ . ^ . end of customize things . ^ . ^ . ^ . ^ . ^ . ^ . ^ . ^ . ^ .
# . . . try to get previously stored settings values to replace above . . .

# . v . v . the program starts here . v . v . v . v . v . v . v . v . v .
#
vagrant_command = ARGV[0]
vagrant_object = ARGV.length > 1 ? ARGV[1] : ""  # the name (if any) of the vagrant VM for this command

# Bridged networks make the machine appear as another physical device on your network.
# We must supply a list of names to avoid Vagrant asking for interactive input
#
if (RUBY_PLATFORM=~/darwin/i)  # on Mac OS, guess two frequently used ports
  interface_guesses = ['en0: Ethernet', 'en1: Wi-Fi (AirPort)']
else  # Windows or Linux
  interface_guesses = settings['interface_name']
end
if ARGV[0] == "up" or ARGV[0] == "reload"
puts "Running on host #{VAGRANT_HOST_NAME}"
puts "Will try bridge network using interface(s): #{interface_guesses}"
end

Vagrant.configure(2) do |config|  # the literal "2" is required.
  info = Etc.getpwnam(login)

  config.ssh.forward_agent = true

  config.vm.provision "shell", inline: "ip address", run: "always"  # what did we get?

  # Now ... just in case our user is running some flavor of VMWare, we will
  # set up his VM, too. But first we need to discover his Host OS ...
  if (/darwin/ =~ RUBY_PLATFORM) != nil
    vmware = "vmware_fusion"
  else
    vmware = "vmware_workstation"
  end
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
    quail_config.vm.provider vmware do |v|  # only for VMware boxes
        v.vmx["memsize"] = "1024"
        v.vmx["numvcpus"] = "1"
	end
  end


  # . . . . . . .  Define the BEVYMASTER . . . . . . . . . . . . . . . .
  config.vm.define "bevymaster", autostart: false do |master_config|
    master_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    master_config.vm.hostname = "bevymaster"
    master_config.vm.network "private_network", ip: NETWORK + ".2.2"  # your host machine will be at NETWORK.2.1
    master_config.vm.network "public_network", bridge: interface_guesses, mac: "be0000" + bevy_mac
    master_config.vm.synced_folder ".", "/vagrant", :owner => "vagrant", :group => "staff", :mount_options => ["umask=0002"]

    if vagrant_command == "ssh"
      master_config.ssh.username = my_linux_user  # if you type "vagrant ssh", use this username
      master_config.ssh.private_key_path = Dir.home() + "/.ssh/id_rsa"
    end

    master_config.vm.provider "virtualbox" do |v|
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.32/27"]  # do not use 10.0 network for NAT
    end

    master_config.vm.provider vmware do |v|
        v.vmx["memsize"] = "1024"
        v.vmx["numvcpus"] = "1"
	end

    script = "mkdir -p /srv/pillar\n"  # put a skeleton /srv on the new master
    script += "mkdir -p /srv/salt/ssh_keys\n"
    script += "chown -R vagrant:staff /srv\n"
    script += "chmod -R 775 /srv\n"
    master_config.vm.provision "shell", inline: script

    master_config.vm.provision :salt do |salt|
       # # #  --- error in salt bootstrap when using git 11/1/17
       salt.install_type = "git v2018.2" # 9865a31e62dcf6b7d6184777483685e4f054168b"  # TODO: use "stable" when OXYGEN is released
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
    quail_config.vm.provider vmware do |v|
        v.vmx["memsize"] = "1024"
        v.vmx["numvcpus"] = "1"
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
    quail_config.vm.provider vmware do |v|
        v.vmx["memsize"] = "1024"
        v.vmx["numvcpus"] = "1"
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
        v.name = BEVY + '_quail42'  # ! N.O.T.E.: name must be unique
        v.memory = 4000       # limit memory for the virtual box
        v.cpus = 2
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.96/27"]  # do not use 10.0 network for NAT
    end
    quail_config.vm.provider vmware do |v|
        v.vmx["memsize"] = "5000"
        v.vmx["numvcpus"] = "2"
    end
    quail_config.vm.provision :salt do |salt|
       # # #  --- error in salt bootstrap when using git 11/1/17
       salt.install_type = "-f git" # b7c0182d93a1092b7369eedfbcf5bc2512c12f1b"  # TODO: use "stable" when OXYGEN is released
       # # #  ---
       salt.verbose = false
       salt.colorize = true
       salt.bootstrap_options = "-A " + NETWORK + ".2.2 -i quail42 -F -P " # -g https://github.com/vernondcole/salt.git"
       salt.masterless = true  # the provisioning script is masterless
    end
  end
end
