#!/usr/bin/env python3
# encoding: utf-8-
# vim:softtabstop=4:ts=4:sw=4:expandtab:tw=120
"""
A utility program to install a SaltStack minion, and optionally, a master with cloud controller.

Maintenance command-line switches:
  --no-sudo = Do not attempt to run with elevated privileges.
  --no-read-settings = Do not read an existing BEVY_SETTINGS_FILE
"""
import subprocess, os, getpass, json, socket, platform, ipaddress, sys, shutil
from pathlib import Path
from urllib.request import urlopen

import yaml
import ifaddr

import pwd_hash
import sudo

argv = [s.strip() for s in sys.argv]
if '--help' in argv:
    print(__doc__)
    exit()
if '--no-sudo' not in argv:  # "off" switch for testing
    sudo.run_elevated()  # Run this script using Administrator privileges

# # # # #
# This program attempts to establish a DRY single source of truth as the file
BEVY_SETTINGS_FILE_NAME = '/srv/pillar/01_bevy_settings.sls'
# That should actually work in many (but not all) cases. It can be extended to more cases.
# We will attempt to keep the /srv directory mapped to local Vagrant VMs as "/srv" so the settings will be
# seen in both environments. Normal minions will receive their settings from the Bevy Master.
# If the Bevy Master is a stand-alone server, it might be a "good idea" to connect its /srv directory to
# the /srv directory on your Workstation using a deployment engine such as PyCharm's.
#
# .. A given machine in the Bevy could be a Workstation, a bevy_master (perhaps as a local VM on a workstation),
# or a bevy minion which is a headless server for some service (perhaps also as a local VM).
# Any of these (except a local VM) might very possibly already have been a minion of some other Salt Master
# before our bevy arrives on the scene. We may want to preserve that minion's connection.
# We will attempt to detect that situation, and we will use the setting "run_second_minion" (which may contain
# "False" or a literal "2") to allow both minions to operate side-by-side.
#  It might work to have run_second_minion be any of the values "2" through "Z", in case
# we are running three or more minions, but that situation would be really weird.
# # # # #

MINIMUM_SALT_VERSION = "2017.7.0-764"  # ... as a string... the month will be integerized below
SALT_BOOTSTRAP_URL = "http://bootstrap.saltstack.com/develop/bootstrap-salt.sh"
# TODO: use release version - "http://bootstrap.saltstack.com/stable/bootstrap-salt.sh"
# SALT_DOWNLOAD_SOURCE = " -g https://github.com/vernondcole/salt git saltify-wol-fix-ping"
SALT_DOWNLOAD_SOURCE = "git develop"
# TODO: use release version when Salt "Oxygen" version is released

# the path to the user definition file will change if two minions are running, hence the "{}"
FROM_BOOTSTRAP_FILE_NAME = '/etc/salt{}/minion.d/01_settings_from_bootstrap.conf'

SALT_SRV_ROOT = '/srv/salt'
SALT_PILLAR_ROOT = '/srv/pillar'
USER_SSH_KEY_FILE_NAME = SALT_SRV_ROOT + '/ssh_keys/{}.pub'

DEFAULT_VAGRANT_PREFIX = '172.17'  # first two bytes of Vagrant private network
DEFAULT_VAGRANT_NETWORK = '172.17.0.0/16'  #  Vagrant private network

DEFAULT_FQDN_PATTERN = '{}.{}.test' # .test is ICANN reserved for test networks.

minimum_salt_version = MINIMUM_SALT_VERSION.split('.')
minimum_salt_version[1] = int(minimum_salt_version[1])  # use numeric compare of month field


def read_bevy_settings_file():
    if '--no-read-settings' in argv:
        return {}
    prov_file = Path(BEVY_SETTINGS_FILE_NAME)
    try:
        print("Trying settings from {}".format(prov_file))
        with prov_file.open() as provision_file:
            stored_settings = yaml.safe_load(provision_file.read()) or {}
    except (OSError, yaml.YAMLError) as e:
        print("Unable to read previous values from {} --> {}.".format(BEVY_SETTINGS_FILE_NAME, e))
        stored_settings = {}
    return stored_settings


def write_bevy_settings_file(settings: dict):
    bevy_settings_file_name = Path(BEVY_SETTINGS_FILE_NAME)
    # python 3.4
    os.makedirs(str(bevy_settings_file_name.parent), exist_ok=True)
    # python 3.5
    # bevy_settings_file_name.parent.mkdir(parents=True, exist_ok=True)

    with bevy_settings_file_name.open('w') as f:
        this_file = Path(__file__).resolve()
        f.write('# this file was created by {}\n'.format(this_file))
        f.write('# Edits here will become the new default values.\n')
        for name, value in settings.items():
            f.write("{}: '{}'\n".format(name, value))
    print('File "{}" written.'.format(bevy_settings_file_name))
    print()

def write_local_minion_config_file():
    '''
    writes a copy of the template, below, into a file named "minion" in this (the default) directory
    substituting the actual path to the ../bevy_srv salt and pillar subdirectories,
    -- which will be used as the Salt minion configuration during the "salt_state_apply" function below.
    '''
    template = """
# stub minion configuration file for stand-alone bevy master bootstrapping.
#
# also used as the default to start building a virgin configuration record
#
master: localhost

file_client: local  # run as masterless

file_roots:    # states are searched in the given order -- first found wins
  base:
    - /vagrant/bevy_srv/salt
    - '{bevy_root}'
    - /srv/salt
top_file_merging_strategy: same  # do not merge the top.sls file from srv/salt

pillar_roots:  # all pillars are merged -- the last entry wins
  base:
    - '{bevy_pillar}'
    - /vagrant/bevy_srv/pillar
    - /srv/pillar
pillar_source_merging_strategy: recurse

file_ignore_regex:
  - '/\.git($|/)'

fileserver_backend:
  - roots

grains:
  datacenter: bevy
  environment: dev
  roles:
    - bevy_member
"""
    file_names = {'bevy_root': Path('../bevy_srv/salt').resolve(),
                  'bevy_pillar': Path('../bevy_srv/pillar').resolve()}
    with open('minion', 'w') as config_file:
        config_file.write(
            template.format(**file_names))


def salt_state_apply(salt_state, **kwargs):
    '''
    Run a salt state using a standalone minion

    :param salt_state: Salt state command to send
    :param kwargs: keyword arguments ...
        expected keyword argements are:
           file_root: a salt fileserver environment.
           pillar_root: a Pillar environment.
           config_dir: a minion configuration environment.
        all other kwargs are assembled as pillar data.
    :return: None
    '''

    file_root = kwargs.pop('file_root', '')
    pillar_root = kwargs.pop('pillar_root', '')
    config_dir = kwargs.pop('config_dir', '')

    command_args = {'salt_state': salt_state,
                    'file_root': '--file-root={}'.format(file_root) if file_root else "",
                    'pillar_root': '--pillar-root={}'.format(pillar_root) if pillar_root else "",
                    'config_dir': '--config-dir={}'.format(config_dir) if config_dir else '',
                    'pillar_data': 'pillar="{!r}"'.format(kwargs) if kwargs else ''}

    cmd = "salt-call --local state.apply {salt_state} --retcode-passthrough " \
          "--state-output=mixed " \
          "{file_root} {pillar_root} {config_dir} --log-level=info " \
          "{pillar_data} ".format(**command_args)

    print(cmd)
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        print("Success")
    else:
        print('Error {} occurred while running Salt state "{}"'.format(
               ret, salt_state if salt_state else "highstate"))


def salt_call_json(salt_command):
    cmd = 'salt-call {} --local --out=json'.format(salt_command)
    print(cmd)
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        print('Error code %d returned from Salt command %r"' % (
            e.returncode, cmd))
        out = b''
    out = out.decode()
    left = out.find('{')  # locate the actual json within the (Windows) response
    right = out.rfind('}')
    try:
        ret = json.loads(out[left:right + 1])
        return ret
    except json.decoder.JSONDecodeError:
        print("JSON error loading ==>", out)


# noinspection PyShadowingNames
def get_ip_choices():
    """
    lists the addresses and names of available network interfaces
    :return: list of dicts {'addr', 'name', 'prefix'}
    addr is the IPv4 or IPv6 network address
    name is the "nice" name.
    prefix is the number of bits in the network prefix
    """
    adapters = ifaddr.get_adapters()
    rtn = []
    for adapter in adapters:
        for ip in adapter.ips:
            if isinstance(ip.ip, str):  # IPv4
                rtn.append({"addr": ipaddress.IPv4Address(ip.ip),
                            "name": adapter.nice_name,
                            "prefix": ip.network_prefix})
            else:  # IPv6
                rtn.append({"addr": ipaddress.IPv6Address(ip.ip[0]),
                            "name": adapter.nice_name,
                            "prefix": ip.network_prefix})
    return rtn


def salt_minion_version():
    try:
        out = salt_call_json("test.version")
        version = out['local'].split('.')
        version[1] = int(version[1])
    except (IndexError, subprocess.CalledProcessError, TypeError):
        print("salt-minion not installed or no output")
        version = ['', 0, '']
    return version


def affirmative(yes, default=False):
    '''
     returns True if user typed "yes"
    '''
    if len(yes) == 0:
        return default
    try:
        return yes.lower().startswith('y')
    except AttributeError:
        return default


def salt_install(master=True):
    print("Checking Salt Version...")
    _current_salt_version = salt_minion_version()
    if _current_salt_version >= minimum_salt_version:
        print("Success: %s" % _current_salt_version)
    else:
        if platform.system() != 'Linux':
            print()
            print('Sorry! Cannot automatically install Salt on your'
                  '"{}" system)'.format(platform.system()))
            print('Please install Salt version {}'.format(MINIMUM_SALT_VERSION))
            print('or later, according to the instructions in the README text,')
            print('and then re-run this script. ...')
            if affirmative(input('... unless,  Salt is already installed and it is Okay to continue? [y/N]:')):
                return True
            write_bevy_settings_file(settings)  # keep the settings we have already found
            exit(1)
        _salt_install_script = "/tmp/bootstrap-salt.sh"
        print("Downloading Salt Bootstrap to %s" % _salt_install_script)
        with open(_salt_install_script, "w+") as f:
            f.write(urlopen(SALT_BOOTSTRAP_URL).read().decode())
        print("Download complete from {}".format(SALT_BOOTSTRAP_URL))
        print("Bootstrapping Salt")
        command = "{} {} -P -X -c /tmp {}".format(
            _salt_install_script,
            '-L -M ' if master else '',
            SALT_DOWNLOAD_SOURCE)
        try:
            print("sudo sh {}".format(command))
            ret = subprocess.call("sudo sh {}".format(command), shell=True)

            print("Salt Installation script done.")
        except OSError as ex:
            print(ex)
            raise ex
        return ret == 0  # flag that we installed Salt


def request_bevy_username_and_password(master: bool, user_name: str):
    """
    get user's information so that we can build a user for her on each minion

    :param master: whether we are installing a salt-master here
    :param user_name: system default user name
    """
    bevy = my_linux_user = pub_key = ''
    loop = Ellipsis  # Python trivia: Ellipsis evaluates as True
    while loop:
        print()
        my_bevy = settings.get('bevy', 'bevy01')
        bevy = input("Name your bevy: [{}]:".format(my_bevy)) or my_bevy
        print()

        default_user = settings.get('my_linux_user') or user_name
        print('Please supply your desired user name to be used on all minions.')
        if master:
            print(' Hint: "vagrant" will be automatically created, too.')
        print('(Hit <enter> to use "{}")'.format(default_user))
        my_linux_user = input('User Name:') or default_user
        print()

        if pwd_hash.hashpath.exists() and loop is Ellipsis:
            print('(using the password hash from {}'.format(pwd_hash.hashpath))
        else:
            pwd_hash.make_file()  # asks your user to type a password, then stores the hash.
            pwd_hash.hashpath.chmod(0o666)
        loop = not affirmative(
            input('Use user name "{}" in bevy "{}"'
                  '? [Y/n]:'.format(my_linux_user, bevy)),
            default=True)  # stop looping if done

    if master:
        pub = None  # object to contain the user's ssh public key
        okay = 'n'
        try:
            user_home_pub = Path.home() / '.ssh' / 'id_rsa.pub'  # only works on Python 3.5+
        except AttributeError:  # older Python3
            user_home_pub = Path('/home/') / getpass.getuser() / '.ssh' / 'id_rsa.pub'
        if master_host:
            user_key_file = Path(SALT_SRV_ROOT) / 'ssh_keys' / (user_name + '.pub')
        else:
            user_key_file = Path(USER_SSH_KEY_FILE_NAME.format(user_name))
        try:  # named user's default location on this machine?
            print('trying file: "{}"'.format(user_home_pub))
            pub = user_home_pub.open()
        except OSError:
            try:  # maybe it is already in the /srv tree?
                user_home_pub = user_key_file
                print('trying file: "{}"'.format(user_home_pub))
                pub = user_home_pub.open()
            except OSError:
                print('No ssh public key found. You will have to supply it the hard way...')
        if pub:
            pub_key = pub.read()
            okay = input(
                '{} exists, and contains:"{}"\n  Use that on all minions? [Y/n]:'.format(
                    user_home_pub, pub_key))

        while not affirmative(okay, default=True):
            print('Next, cut the text of your ssh public key to transmit it\n')
            print('to your new server.\n')
            print('You can usually get it by typing:\n')
            print('   cat ~/.ssh/id_rsa.pub\n')
            print()
            pub_key = input('Paste it here --->')
            print('.......... (checking) ..........')
            if len(pub_key) < 64:
                print('too short!')
                continue
            print('I received ===>{}\n'.format(pub_key))
            okay = input("Use that? ('exit' to bypass ssh keys)[Y/n]:")
            if affirmative(okay) or okay.lower() == 'exit':
                break
        if affirmative(okay, default=True):
            # user_key_file.parent.mkdir(parents=True, exist_ok=True) # only works for Python3.5+
            os.makedirs(str(user_key_file.parent), exist_ok=True)  # 3.4
            # 3.5 user_key_file.write_text(pub_key)
            with user_key_file.open('w') as f:  # 3.4
                f.write(pub_key)  # 3.4
                print('file {} written.'.format(str(user_key_file)))
    return bevy, my_linux_user


def get_salt_master_id():
    out = salt_call_json("config.get master")
    try:
        master_id = out['local']
    except KeyError:
        master_id = "!!No answer from salt-call!!"
    ans = master_id[0] if isinstance(master_id, list) else master_id
    print('configured master now = "{}"'.format(master_id))
    return ans


def choose_master_address(host_name):
    default = host_name
    if master:
        choices = get_ip_choices()
        print('This machine has the following IP addresses:')
        for ip in choices:
            if not ip['addr'].is_loopback and not ip['addr'].is_link_local:
                print('{addr}/{prefix} - {name}', **ip)
    try:
        ip_ = socket.getaddrinfo(default, 4506, type=socket.SOCK_STREAM)
        print('The name {} translates to {}'.format(host_name, ip_[0][4][0]))
    except (socket.error, IndexError):
        pass
    while Ellipsis:  # repeat until user types a valid entry
        resp = input("What default url address for the master? [{}]:".format(default))
        choice = resp or default
        try:  # look up the address we have, and see if it appears good
            ip_ = socket.getaddrinfo(choice, 4506, type=socket.SOCK_STREAM)
            addy = ip_[0][4][0]
            print("Okay, the bevy master's address returns as {}".format(addy))
            return choice  # it looks good -- exit the loop
        except (socket.error, IndexError, AttributeError):
            print('"{}" is not a valid IP address.'.format(choice))


def choose_vagrant_network():
    while Ellipsis:
        network = settings['vagrant_network']
        resp = input(
            'What is your desired Vagrant internal network? [{}]:'.format(network))
        network = resp or network
        try:
            ip_net = ipaddress.ip_network(network, strict=False)
        except ipaddress.NetmaskValueError:
            print('Invalid network string. Try again.')
            continue
        if not ip_net.is_private:
            print('Sorry, internal network must be private.')
            continue
        try:
            if ip_net.version == 4:
                prefix = '.'.join(str(ip_net).split('.')[0:2])  # the first two octets of the network
            else:
                prefix = ip_net.compressed.partition("::")[0:2]  # leave out the part after the "::"
        except Exception as e:
            print(e)
            continue
        return prefix, network  # break out of loop if no errors


def choose_bridge_interface():
    host_network = ipaddress.ip_network(settings['vagrant_network'])
    choices = []
    for ip in get_ip_choices():
        addy = ip['addr']
        if addy.is_loopback or addy.is_link_local:
            continue
        if addy in host_network:
            continue
        choices.append(ip)
    while Ellipsis:
        print('This machine has the following possible external IP addresses:')
        i = 0
        for ip in choices:
            i += 1
            print(i, ': {addr}/{prefix} - {name}'.format(**ip), sep='')
        if i == 0:
            raise RuntimeError('Sorry. No external IP interfaces found.')
        if i == 1:
            print('Will use the only possible choice.')
            return choices[0]
        else:
            try:
                choice = choices[int(input('Which one do you want to use?:')) - 1]
                return choice
            except (ValueError, IndexError, AttributeError):
                print('Bad choice.')


def get_linux_password():
    ''' retrieve stored bevy ssl password hash '''
    # 3.5 linux_password = pwd_hash.hashpath.read_text().strip()
    with pwd_hash.hashpath.open() as f:  # 3.4
        linux_password = f.read().strip()  # 3.4
    return linux_password


if __name__ == '__main__':
    settings = {}
    user_name = getpass.getuser()

    if user_name == 'root':
        user_name = os.environ['SUDO_USER']

    settings = read_bevy_settings_file()
    try:
        import pwd  # works on Posix only
        pwd_entry = pwd.getpwnam(user_name)  # look it up the hard way -- we are running SUDO
        settings.setdefault('my_linux_uid', pwd_entry[2])  # useful for network shared files
        settings.setdefault('my_linux_gid', pwd_entry[3])
    except (ImportError, IndexError, AttributeError):
        settings.setdefault('my_linux_uid', '')
        settings.setdefault('my_linux_gid', '')

    settings.setdefault('vagrant_prefix', DEFAULT_VAGRANT_PREFIX)
    settings.setdefault('vagrant_network', DEFAULT_VAGRANT_NETWORK)
    try:
        desktop = Path.home() / "Desktop"  # try for a /home/<user>/Desktop directory
        on_a_workstation = desktop.exists()
    except AttributeError:
        on_a_workstation = False  # blatant assumption: Python version is less than 3.5, therefore not a Workstation

    master_host = False  # assume this machine is NOT the VM host for the Master
    print('This program can make this machine a simple workstation to join the bevy')
    if platform.system() != 'Windows':
        print('or a bevy salt-master (including cloud-master),')
    if on_a_workstation:
        print('or a Vagrant host, hosting a bevy master.')
        recommendation = ' (not recommended)'
    else:
        recommendation = ''
    master = platform.system() != 'Windows' and affirmative(
        input('Should this machine BE the master?{} [y/N]:'))
    if not master and on_a_workstation:
        master_host = affirmative(input(
            'Will the Bevy Master be a VM guest of this machine? [y/N]:'.format(recommendation)))

    my_directory = Path(os.path.dirname(os.path.abspath(__file__)))
    bevy_root_node = (my_directory / '../bevy_srv').resolve()  # this dir is part of the Salt file_roots dir
    if not bevy_root_node.is_dir():
        raise SystemError('Unexpected situation: Expected directory not present -->{}'.format(bevy_root_node))

    bevy, settings['my_linux_user'] = request_bevy_username_and_password(master or master_host, user_name)
    settings['bevy'] = bevy
    print('Setting up user "{}" on bevy "{}"'.format(settings['my_linux_user'], bevy))

    # check for use of virtualbox and Vagrant
    # test for Vagrant being already installed
    rtn = subprocess.call('vagrant -v', shell=True) if on_a_workstation else NotImplemented
    vagrant_present = rtn == 0

    settings['cwd'] = settings['runas'] = settings['vagranthost'] = ''
    virtualbox_install = False
    while Ellipsis:  # repeat until user says okay
        virtualbox_install = False
        settings['vagranthost'] = ''  # node ID of Vagrant host machine
        isvagranthost = master_host or on_a_workstation and affirmative(input(
            'Will this machine be a bevy host for Vagrant virtual machines? [y/N]:'))
        if isvagranthost:
            if master:
                settings['vagranthost'] = 'bevymaster'
            else:
                settings['vagranthost'] = platform.node().split('.')[0]
            virtualbox_install = False if vagrant_present else affirmative(input(
                'Do you wish to install VirtualBox and Vagrant? [y/N]:'))
        elif master:
            print('What is/will be the Salt node id of the Vagrant host machine?')
            settings['vagranthost'] = input('(Leave blank if none.):')
            if settings['vagranthost']:
                try:
                    socket.inet_aton(settings['vagranthost'])  # an exception is expected and is correct
                    print('Please enter a node ID, not an IP address.')
                    continue  # user committed an entry error ... retry
                except OSError:
                    pass  # entry was not an IP address.  Good.
        if settings['vagranthost']:
            resp = input(
                'What user on {} will own the Vagrantbox files?'
                ' [{}]:'.format(settings['vagranthost'], settings['my_linux_user']))
            settings['runas'] = resp or settings['my_linux_user']

            parent = os.path.abspath('..')
            resp = input(
                'What is the full path to the Vagrantfile on {}?'
                '[{}]:'.format(settings['vagranthost'], parent))
            settings['cwd'] = resp or parent
            print()
            print('Using "{}" on node "{}"'.format(
                os.path.join(settings['cwd'], 'Vagrantfile'),
                settings['vagranthost']
            ))
            print('owned by {}.'.format(settings['runas']))
            if vagrant_present:
                print('Vagrant is already presesent on this machine.')
            else:
                print('VirtualBox and Vagrant {} be installed'.format(
                    'will' if virtualbox_install else 'will not'))
        else:
            print('No Vagrant Box will be used.')
        if affirmative(input('Correct? [Y/n]:'), default=True):
            break
    if settings['vagranthost']:
        settings['vagrant_prefix'], settings['vagrant_network'] = choose_vagrant_network()
        choice = choose_bridge_interface()
        settings['vagrant_interface_guess'] = choice['name']

    settings.setdefault('fqdn_pattern',  DEFAULT_FQDN_PATTERN)

    we_installed_it = salt_install()  # download & run salt

    if we_installed_it:
        run_second_minion = False
        master_id = 'salt'
    else:
        master_id = get_salt_master_id()
        if master_id is None or master_id.startswith('!'):
            raise ValueError('Something wrong. Salt master should be known at this point.')
        run_second_minion = master_id not in ['localhost', 'salt', '127.0.0.1']
    if run_second_minion:
        print('Your Salt master id was detected as: {}'.format(master_id))
        print('You may continue to use that master, and add a second master for your bevy.')
        run_second_minion = affirmative(input('Do you wish to run a second minion? [y/N]:'))
    two = '2' if run_second_minion else ''
    if platform.system() == 'Windows':
        master_pub = Path(r'C:\salt{}\conf\pki\minion\minion_master.pub'.format(two))
    else:
        master_pub = Path('/etc/salt{}/pki/minion/minion_master.pub'.format(two))
    try:  # forget a former master's key (if any)
        print('Removing master public key "{}"'.format(master_pub))
        master_pub.unlink()
    except (FileNotFoundError, PermissionError):
        pass

    # if there is no top.sls, copy ours to make a start
    if not os.path.exists(SALT_SRV_ROOT + 'top.sls'):
        print('Creating a new default {}/top.sls'.format(SALT_SRV_ROOT))
        os.makedirs(SALT_SRV_ROOT, exist_ok=True)  # 3.4
        shutil.copy('../bevy_srv/salt/top.sls', SALT_SRV_ROOT)
    if not os.path.exists(SALT_PILLAR_ROOT + 'top.sls'):
        print('Creating a new default {}/top.sls'.format(SALT_PILLAR_ROOT))
        os.makedirs(SALT_PILLAR_ROOT, exist_ok=True)  # 3.4
        shutil.copy('../bevy_srv/pillar/top.sls', SALT_PILLAR_ROOT)

    master_address = choose_master_address(settings.get('bevymaster_url', master_id))
    settings['bevymaster_url'] = master_address

    if master_host:
        settings.setdefault('master_vagrant_ip', settings['vagrant_prefix'] + '.2.2')

    write_local_minion_config_file()

    settings.setdefault('force_linux_user_password', True)
    settings['linux_password_hash'] = get_linux_password()
    write_bevy_settings_file(settings)

    if master:
        print('\n\n. . . . . . . . . .\n')
        salt_state_apply('',  # blank name means: apply highstate
                         config_dir=str(my_directory.resolve()),
                         bevy_root=str(bevy_root_node),
                         bevy=bevy,
                         node_name='bevymaster',
                         bevymaster_url=master_address,
                         run_second_minion=run_second_minion,
                         vbox_install=virtualbox_install,
                         vagranthost=settings['vagranthost'],
                         runas=settings['runas'],
                         cwd=settings['cwd'],
                         doing_bootstrap=True,  # initialize environment
                         )

    else:  # not making a master, make a minion
        if master_host:
            my_master_url = settings['master_vagrant_ip']
        else:
            my_master_url = settings['bevymaster_url']
        while Ellipsis:  # loop until user says okay
            print('Trying {} for bevy master'.format(my_master_url))
            try:  # look up the address we have, and see if it appears good
                ip_ = socket.getaddrinfo(my_master_url, 4506, type=socket.SOCK_STREAM)
                okay = input("Use {} as this machine's bevy master address? [Y/n]:".format(ip_[0][4][0]))
                if affirmative(okay, True):
                    if master_host and my_master_url != settings['master_vagrant_ip']:
                        if affirmative(input('Also use as the default Vagrant master address? [Y/n]:', True)):
                            settings['master_vagrant_ip'] = my_master_url
                            write_bevy_settings_file(settings)
                    break  # it looks good -- exit the loop
            except (socket.error, IndexError):
                pass  # looks bad -- ask for another
            my_master_url = input("Try again. Type the name or address of this machine's bevy master?:")

        print('\n\n. . . . . . . . . .\n')
        node_name = platform.node().split('.')[0]  # your workstation's hostname
        salt_state_apply('configure_bevy_member',
                         config_dir=str(my_directory.resolve()),
                         bevy_root=str(bevy_root_node),
                         bevy=bevy,
                         bevymaster_url=my_master_url,
                         node_name=node_name,
                         run_second_minion=run_second_minion,
                         vbox_install=virtualbox_install,
                         my_linux_user=settings['my_linux_user'],
                         vagranthost=settings['vagranthost'],
                         runas=settings['runas'],
                         cwd=settings['cwd'])
    print()
    print('{} done.'.format(__file__))
    print()
    if platform.system() == 'Windows':
        input('Hit <Enter> to close this window:')
