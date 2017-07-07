# -*- mode: ruby -*-
# vi: set ft=ruby :

# this configuration file is written in Ruby.
# I had to spend a day learning enough Ruby to add smart features,
# so if it is not particularly good Ruby code, I'm sorry. -- VDC

require 'etc'  # import a Ruby module used to get your user info

# your environment needs a name. This will define it...
BEVY = "bevy1"
DOMAIN = BEVY + ".test"
BEVYMASTER = "bevymaster." + DOMAIN

# let's use your own username (from this workstation) as the log-in user
# on each of your Salt minions.
# .. In order to log in, or approve an action, you may need
# .. to type your password.  When Salt configures your minions,
# .. it will install the password hash (defined here) on each minion.
# .. You can create a hash using the included pwd_hash.py script.
HASHFILE_NAME = 'bevy_linux_password.hash'
hash_path = File.join(Dir.home, '.ssh', HASHFILE_NAME)

VAGRANT_COMMAND = ARGV[0]  # the "xxx" from "vagrant xxx yyy zzz"

Vagrant.configure(2) do |config|
  login = Etc.getlogin    # get your own user info to use in the VM
  info = Etc.getpwnam(login)

  config.ssh.forward_agent = true

  # Creates a private network, using hard-assigned private IP addresses.
  # These assresses will also be hard-assigned in Salt configuration files.
  # If you change these addresses, also change them in Salt.
  # Your host workstation will be at x.x.x.1 (172.17.2.1) on that network.


  # . . . . .  . Configuration for the Salt (and salt-cloud) master . . . . . . .
  config.vm.define "bevymaster", primary: true do |master_config|
    # if you want to change what OS your VM will be running, do it here ...
    master_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box

    master_config.vm.hostname = BEVYMASTER
    
    # the Salt master is expected to be at this address...
	master_config.vm.network "private_network", ip: "172.17.2.2"

    # kludge to enable guest VM user to use your credentials
    master_config.vm.synced_folder "~", "/my_home", :group => "staff", :mount_options => ["umask=0002"]
 
    # used for configuration. your bevy_srv subfolder will appear on the VM as /srv
    master_config.vm.synced_folder "bevy_srv", "/srv", :group => "staff", :mount_options => ["umask=0002"]

	# as a convenience, this directory will appear on your VM as /vagrant
    master_config.vm.synced_folder ".", "/vagrant", :owner => "vagrant", :group => "staff", :mount_options => ["umask=0002"]

    if VAGRANT_COMMAND == "ssh"
        master_config.ssh.username = login  # if you type "vagrant ssh", use your own username
        master_config.ssh.private_key_path = info.dir + "/.ssh/id_rsa"
        master_config.ssh.forward_agent = true
    end

    master_config.vm.provider "virtualbox" do |v|  # configuration for a Virtualbox VM 
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1            # the Salt master does not need much power
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", "172.17.1/24"]  # do not use 10.0 network for NAT
	end
    master_config.vm.provider "vmware" do |v|  # now say it again in case we use e.g. --provider=vmware_fusion
        v.memory = 1024       # limit machine size for the vmware box, too
        v.cpus = 1
		v.linked_clone = true
	end

    # to provision this VM we will first run a shell script...
    script = "mkdir -p /srv/pillar\n"
    script += "echo '# placeholder file created by Vagrant provision' > /srv/pillar/my_user_settings.sls"
    master_config.vm.provision "shell", inline: script

    # the hard work will next be done by running a stand-alone Salt minion on it...
    master_config.vm.provision :salt do |salt|
        salt.install_type = "stable"
        salt.verbose = true
        salt.colorize = true
        salt.bootstrap_options = "-M -P -X -c /tmp"  # install salt-master and minion, do not start them
        salt.masterless = true  # the provisioning script for the master is masterless
        salt.run_highstate = true  # run a Salt "highstate" to do the provisioning
        salt.minion_config = "configure_master/minion"  # find the configuration here

	  
		# read the password hash file from your workstation
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
        salt.pillar({                 # configure a new interactive user on the new VM
          "my_linux_user" => login,
          "my_linux_uid" => info.uid,
          "my_linux_gid" => info.gid,
          "bevy" => BEVY,
          "bevymaster_name" => BEVYMASTER,
          "run_second_minion" => false,
          "linux_password_hash" => password_hash,
          "force_linux_user_password" => true
                    }
        )
        if VAGRANT_COMMAND == "up" 
            puts "password_hash=#{password_hash}"
        end
    end
  end



  # . . . . . . . . Configuration for the first minion "quail16" running Ubuntu 16.04 . . . . . . . . .
  config.vm.define "quail16", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/xenial64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail16." + DOMAIN
    quail_config.vm.network "private_network", ip: "172.17.2.3"  # needed so saltify_profiles.conf can find this unit
    quail_config.vm.synced_folder ".", "/vagrant", disabled: true  # do not use the default shared directory

    quail_config.vm.provider "virtualbox" do |v|
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", "172.17.3/24"]  # do not use 10.0 network for NAT
	end
    quail_config.vm.provider "vmware" do |v|
        v.memory = 1024       # limit memory for the vmware box, too
        v.cpus = 1
		v.linked_clone = true # make a soft copy of the base Vagrant box
	end
    quail_config.vm.provision :shell, path: "vagrant_quail_provision.sh"
  end


  # . . . . . . . .  Configuration for the second minion "quail14" running Ubuntu 14.04 . . . . . . 
  config.vm.define "quail14", autostart: false do |quail_config|
    quail_config.vm.box = "boxesio/trusty64-standard"  # a public VMware & Virtualbox box
    quail_config.vm.hostname = "quail14." + DOMAIN
    quail_config.vm.network "private_network", ip: "172.17.2.4"  # needed so saltify_profiles.conf can find this unit
    quail_config.vm.synced_folder ".", "/vagrant", disabled: true

    quail_config.vm.provider "virtualbox" do |v|
        v.memory = 1024       # limit memory for the virtual box
        v.cpus = 1
        v.linked_clone = true # make a soft copy of the base Vagrant box
        v.customize ["modifyvm", :id, "--natnet1", "172.17.4/24"]  # do not use 10.0 network for NAT
	end
    quail_config.vm.provider "vmware" do |v|
        v.memory = 1024       # limit memory for the vmware box, too
        v.cpus = 1
		v.linked_clone = true # make a soft copy of the base Vagrant box
	end
    quail_config.vm.provision :shell, path: "vagrant_quail_provision.sh"
  end

end

