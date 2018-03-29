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
# under the DRY principle, the most important setting are stored
# in a Salt 'pillar' file. Vagrant has to look them up there...
#
# . v . v . retrieve stored bevy settings . v . v . v . v . v . v .
BEVY_SETTINGS_FILE_NAME = '/srv/pillar/01_bevy_settings.sls'
if File.exists?(BEVY_SETTINGS_FILE_NAME)
  settings = YAML.load_file(BEVY_SETTINGS_FILE_NAME)
else
  settings = {"bevy" => "xxxx", "vagrant_prefix" => '172.17'}
  if ARGV[0] == "up"
    puts "You must run 'configure_machine/bootstrap_bevy_member_here.py' before running 'vagrant up'"
    abort "Unable to read settings file #{BEVY_SETTINGS_FILE_NAME}."
    end
end
# .
BEVY = settings["bevy"]  # the name of your bevy
# the first two bytes of your Vagrant host-only network IP ("192.168.x.x")
NETWORK = "#{settings['vagrant_prefix']}"
# ^ ^ each VM below will have a NAT network in NETWORK.17.x/27.
puts "Your bevy name:#{BEVY} using local network #{NETWORK}.x.x"
puts "This computer will be at #{NETWORK}.2.1" if ARGV[1] == "up"
bevy_mac = (BEVY.to_i(36) % 0x1000000).to_s(16)  # a MAC address based on hash of BEVY
# in Python that would be: bevy_mac = format(int(BEVY, base=36) % 0x1000000, 'x')
#
# .
BEVYMASTER = "bevymaster"   # the name for your bevy master
# .
VAGRANT_HOST_NAME = Socket.gethostname
login = Etc.getlogin    # get your own user information to use in the VM
my_linux_user = settings['my_linux_user']
HASHFILE_NAME = 'bevy_linux_password.hash'  # filename for your Linux password hash
hash_path = File.join(Dir.home, '.ssh', HASHFILE_NAME)  # where you store it ^ ^ ^
#
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
  interface_guesses = settings['vagrant_interface_guess']
end
if ARGV[0] == "up" or ARGV[0] == "reload"
  puts "Running on host #{VAGRANT_HOST_NAME}"
  puts "Will try bridge network using interface(s): #{interface_guesses}"
end

Vagrant.configure(2) do |config|  # the literal "2" is required.
  info = Etc.getpwnam(login)

  config.ssh.forward_agent = true

  if ARGV.length > 2 and not ARGV[2].start_with? 'win'
    config.vm.provision "shell", inline: "ip address", run: "always"  # what did we get?
  end

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
    quail_config.vm.hostname = "quail1" # + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.8"  # needed so saltify_profiles.conf can find this unit
    if ARGV[0] == "up" and (ARGV.length == 1 or (ARGV.length > 1 and ARGV[1] == "quail1"))
      puts "Starting 'quail1' at #{NETWORK}.2.8..."
      end
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|  # only for VirtualBox boxes
        v.name = BEVY + '_quail1'  # ! N.O.T.E.: name must be unique
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
    master_config.vm.network "private_network", ip: NETWORK + ".2.2"
    if ARGV.length > 1 and ARGV[0] == "up" and ARGV[1] == "bevymaster"
      if settings['master_vagrant_ip'] != NETWORK + ".2.2"
        abort "Sorry. Your master_vagrant_ip setting of '#{settings['master_vagrant_ip']}' suggests that your Bevy Master is not expected to be Virtual here."
        end
      puts "Starting #{ARGV[1]} at #{NETWORK}.2.2..."
      end
    master_config.vm.network "public_network", bridge: interface_guesses, mac: "be0000" + bevy_mac
    master_config.vm.synced_folder ".", "/vagrant", :owner => "vagrant", :group => "staff", :mount_options => ["umask=0002"]
    master_config.vm.synced_folder "/srv", "/srv", :owner => "vagrant", :group => "staff", :mount_options => ["umask=0002"]
    if settings.has_key?('application_roots')  # additional shares for optional applications directories
      settings['application_roots'].each do |share|  # formatted real-path:share-path
        s = share.split(';')
        master_config.vm.synced_folder s[0], "/#{s[1]}", :owner => "vagrant", :group => "staff", :mount_options => ["umask=0002"]
      end
    end

    if vagrant_command == "ssh"
      master_config.ssh.username = my_linux_user  # if you type "vagrant ssh", use this username
      master_config.ssh.private_key_path = Dir.home() + "/.ssh/id_rsa"
    end

    master_config.vm.provider "virtualbox" do |v|
        v.name = BEVY + '_bevymaster'  # ! N.O.T.E.: name must be unique
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.32/27"]  # do not use 10.0 network for NAT
    end

    master_config.vm.provider vmware do |v|
        v.vmx["memsize"] = "1024"
        v.vmx["numvcpus"] = "1"
	end

    script = "mkdir -p /etc/salt/minion.d\n"
    script += "chown -R vagrant:staff /etc/salt/minion.d\n"
    script += "chmod -R 775 /etc/salt/minion.d\n"
    master_config.vm.provision "shell", inline: script
    master_config.vm.provision "file", source: settings['GUEST_MASTER_CONFIG_FILE'], destination: "/etc/salt/minion.d/00_vagrant_boot.conf"

    master_config.vm.provision :salt do |salt|
       # # #  --- error in salt bootstrap when using git 11/1/17
       salt.install_type = "git v2018.3.0rc1"  # TODO: use "stable" when OXYGEN is released
       # # #  ---
       salt.verbose = true
       salt.log_level = "info"
       salt.colorize = true
       salt.bootstrap_options = "-P -M -L "  # install salt-cloud and salt-master
       salt.masterless = true  # the provisioning script for the master is masterless
       salt.run_highstate = true
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
         "bevymaster_url" => NETWORK + '.2.2',
         "run_second_minion" => false,
         "linux_password_hash" => password_hash,
         "force_linux_user_password" => true,
         "vagranthost" => VAGRANT_HOST_NAME,
         "runas" => login,
         "cwd" => Dir.pwd,
         "vbox_install" => false,
         "doing_bootstrap" => true,  # flag for Salt state system
                   }
         )
       end
  end


  # . . . . . . . . . . . . Define machine QUAIL16 . . . . . . . . . . . . . . 
  config.vm.define "quail16", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail16" # + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.3"
    if ARGV.length > 1 and ARGV[0] == "up" and ARGV[1] == "quail16"
      puts "Starting #{ARGV[1]} at #{NETWORK}.2.3..."
      end
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|
        v.name = BEVY + '_quai16'  # ! N.O.T.E.: name must be unique
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
    quail_config.vm.hostname = "quail14" # + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.4"
    if ARGV.length > 1 and ARGV[0] == "up" and ARGV[1] == "quail14"
      puts "Starting #{ARGV[1]} at #{NETWORK}.2.4..."
      end
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|
        v.name = BEVY + '_quail14'  # ! N.O.T.E.: name must be unique
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

 # . . . . . . . . . . . . Define machine win16 . . . . . . . . . . . . . .
 # . this machine has salt installed .
  config.vm.define "win16", autostart: false do |quail_config|
    quail_config.vm.box = "mwrock/Windows2016"  # Windows 2016 server
    # quail_config.vm.hostname = "windowstest"  # use of this setting causes VM to reboot Windows.

    quail_config.vm.network "public_network", bridge: interface_guesses
    quail_config.vm.network "private_network", ip: NETWORK + ".2.16"
    if ARGV.length > 1 and ARGV[0] == "up" and ARGV[1] == "win16"
      puts "Starting #{ARGV[1]} as a Salt minion of #{settings['bevymaster_url']}."
      end

    quail_config.vm.provider "virtualbox" do |v|
        v.name = BEVY + '_win16'  # ! N.O.T.E.: name must be unique
        v.gui = true  # turn on the graphic window
        v.linked_clone = true
        v.customize ["modifyvm", :id, "--vram", "27"]  # enough video memory for full screen
        v.memory = 4096
        v.cpus = 2
    end
    quail_config.vm.guest = :windows
    quail_config.vm.boot_timeout = 300
    quail_config.vm.graceful_halt_timeout = 60
    script = "new-item C:\\salt\\conf\\minion.d -itemtype directory\r\n"
    script += "'master: #{settings['bevymaster_url']}' > C:\\salt\\conf\\minion.d\\00_vagrant_master_address.conf\r\n"
    quail_config.vm.provision "shell", inline: script
    quail_config.vm.provision "file", source: settings['WINDOWS_GUEST_CONFIG_FILE'], destination: "/etc/salt/minion.d/00_vagrant_boot.conf"
    quail_config.vm.provision :salt do |salt|  # salt_cloud cannot push Windows salt
        salt.minion_id = "win16"
        salt.log_level = "info"
        salt.verbose = true
        salt.colorize = true
        salt.run_highstate = true
    end
  end

 # . . . . . . . . . . . . Define machine win12 . . . . . . . . . . . . . .
 # . this machine has salt installed .
  config.vm.define "win12", autostart: false do |quail_config|
    quail_config.vm.box = "devopsguys/Windows2012R2Eval"

    quail_config.vm.network "public_network", bridge: interface_guesses
    quail_config.vm.network "private_network", ip: NETWORK + ".2.12"
    if ARGV.length > 1 and ARGV[0] == "up" and ARGV[1] == "win12"
      puts "Starting #{ARGV[1]} as a Salt minion of #{settings['bevymaster_url']}."
      end

    quail_config.vm.provider "virtualbox" do |v|
        v.name = BEVY + '_win12'  # ! N.O.T.E.: name must be unique
        v.gui = true  # turn on the graphic window
        v.linked_clone = true
        v.customize ["modifyvm", :id, "--vram", "27"]  # enough video memory for full screen
        v.memory = 4096
        v.cpus = 2
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.128/27"]  # do not use 10.0 network for NAT
    end
    quail_config.vm.guest = :windows
    quail_config.vm.boot_timeout = 300
    quail_config.vm.graceful_halt_timeout = 60
    script = "new-item C:\\salt\\conf\\minion.d -itemtype directory\r\n"
    script += "'master: #{settings['bevymaster_url']}' > C:\\salt\\conf\\minion.d\\00_vagrant_master_address.conf\r\n"
    quail_config.vm.provision "shell", inline: script
    quail_config.vm.provision "file", source: settings['WINDOWS_GUEST_CONFIG_FILE'], destination: "/etc/salt/minion.d/00_vagrant_boot.conf"
    quail_config.vm.provision :salt do |salt|  # salt_cloud cannot push Windows salt
        salt.minion_id = "win12"
        salt.log_level = "info"
        salt.verbose = true
        salt.colorize = true
        salt.run_highstate = true
    end
  end

# . . . . . . .  Define quail2 with Salt minion installed . . . . . . . . . . . . . .
# . this machine has Salt installed but no states run or defined.
# . Its master is "bevymaster".
  config.vm.define "quail2", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail2" # + DOMAIN
    quail_config.vm.network "private_network", ip: NETWORK + ".2.5"
    if ARGV.length > 1 and ARGV[0] == "up" and ARGV[1] == "quail2"
      puts "Starting #{ARGV[1]} at #{NETWORK}.2.5 as a Salt minion with master=#{settings['bevymaster_url']}...\n."
      end
    quail_config.vm.network "public_network", bridge: interface_guesses

    quail_config.vm.provider "virtualbox" do |v|
        v.name = BEVY + '_quail2'  # ! N.O.T.E.: name must be unique
        v.memory = 4000       # limit memory for the virtual box
        v.cpus = 2
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", NETWORK + ".17.160/27"]  # do not use 10.0 network for NAT
    end
    quail_config.vm.provider vmware do |v|
        v.vmx["memsize"] = "5000"
        v.vmx["numvcpus"] = "2"
    end

    script = "mkdir -p /etc/salt/minion.d\n"
    script += "chown -R vagrant:staff /etc/salt/minion.d\n"
    script += "chmod -R 775 /etc/salt/minion.d\n"
    quail_config.vm.provision "shell", inline: script
    quail_config.vm.provision "file", source: settings['GUEST_MINION_CONFIG_FILE'], destination: "/etc/salt/minion.d/00_vagrant_boot.conf"
    quail_config.vm.provision :salt do |salt|
       # # #  --- error in salt bootstrap when using git 11/1/17
       salt.install_type = "-f git v2018.3.0rc1"  # TODO: use "stable" when OXYGEN is released
       # # #  ---
       salt.verbose = false
       salt.bootstrap_options = "-A #{settings['bevymaster_url']} -i quail2 -F -P "
       salt.run_highstate = true
    end
  end
end
