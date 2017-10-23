#!/usr/bin/env python3
# encoding: utf-8
# vim:softtabstop=4:ts=4:sw=4:expandtab:tw=120
"""
A utility program to install a SaltStack minion,
and optionally, a master and cloud controller.
"""
import subprocess, os, getpass, json, socket, platform
from pathlib import Path
from urllib.request import urlopen

import pwd_hash  # from the current working directory

MINIMUM_SALT_VERSION = "2017.7.0-758"  # ... as a string... the month will be integerized below
SALT_BOOTSTRAP_URL = "http://bootstrap.saltstack.com/develop/bootstrap-salt.sh"
# TODO: use release version - "http://bootstrap.saltstack.com/stable/bootstrap-salt.sh"
SALT_DOWNLOAD_SOURCE = " git"
# TODO: use release version when Salt "Oxygen" version is released

# the path to the user definition file will change if two minions are running, hence the {}
FROM_BOOTSTRAP_FILE_NAME = '/etc/salt{}/minion.d/01_settings_from_bootstrap.conf'
USER_SETTINGS_PILLAR_FILE = '/srv/pillar/01_bootstrap_settings.sls'

USER_SSH_KEY_FILE_NAME = '/srv/salt/ssh_keys/{}.pub'

# the template for a bevy master fully qualified domain name. The bevy name will be supplied in {}
BEVYMASTER_FQDN_PATTERN = 'bevymaster.{}.test'

minimum_salt_version = MINIMUM_SALT_VERSION.split('.')
minimum_salt_version[1] = int(minimum_salt_version[1])  # use numeric compare of month field


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

    cmdargs = {'salt_state': salt_state}
    cmdargs['file_root'] = '--file-root={}'.format(file_root) if file_root else ""
    cmdargs['pillar_root'] = '--pillar-root={}'.format(pillar_root) if pillar_root else ""
    cmdargs['config_dir'] = '--config-dir={}'.format(config_dir) if config_dir else ''

    cmdargs['pillar_data'] = 'pillar="{!r}"'.format(kwargs) if kwargs else ''

    cmd = "salt-call --local state.apply {salt_state} --retcode-passthrough --state-output=mixed " \
          "{file_root} {pillar_root} {config_dir} --log-file-level=info --log-level=critical " \
          "{pillar_data} ".format(**cmdargs)

    print(cmd)
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        print("Success")
    else:
        print('Error %d occurred while running Salt state "%s"' % (ret,
                                                                   salt_state if salt_state else "highstate"))


def salt_call_json(salt_command):
    cmd = 'salt-call {} --local --out=json'.format(salt_command)
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(e.output)
        print('Error code %d returned from Salt command %r"' % (
            e.returncode, cmd))
        out = b''
    try:
        ret = json.loads(out.decode())
        return ret
    except json.decoder.JSONDecodeError:
        print("JSON error loading ==>", out)


def salt_minion_version():
    try:
        out = subprocess.check_output("salt-call --version", shell=True)
        out = out.decode()
        version = out.split(" ")[1].split('.')
        version[1] = int(version[1])
    except subprocess.CalledProcessError:
        print("salt-minion not installed")
        version = ["", 0, '']
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
    print("Checking Salt Version")
    _current_salt_version = salt_minion_version()
    if _current_salt_version >= minimum_salt_version:
        print("Success: %s" % _current_salt_version)
    else:
        if platform.system() != 'Linux':
            print('Sorry! Cannot automatically install Salt on your'
                  '"{}" system)'.format(platform.system))
            print('Please install Salt version {}'.format(MINIMUM_SALT_VERSION))
            print('or later, according to the instructions in the README text,')
            print('and then re-run this script.')
            exit(78)
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


def request_bevy_username_and_password(master: bool):
    """
    get user's information so that we can build a user for her on each minion

    :type master: bool
    :param master: whether we are installing a salt-master here
    """
    bevy = user_name = pub_key = ''
    loop = Ellipsis  # Python trivia: Ellipsis evaluates as True
    while loop:
        print()
        bevy = input("Name your bevy: {'bevy1'}:") or 'bevy1'
        print()

        print('Please supply your desired user name to be used on all minions.')
        if master:
            print(' Hint: "administrator" and "atomizer" will be automatically created, too.')
        print('(Hit <enter> to use "{}")'.format(default_user))
        user_name = input('User Name:') or default_user
        print()

        #        if master:
        if pwd_hash.hashpath.exists() and loop is Ellipsis:
            print('(using the password hash from {}'.format(pwd_hash.hashpath))
        else:
            pwd_hash.make_file()  # asks your user to type a password, then files the hash.
            pwd_hash.hashpath.chmod(0o666)
        loop = not affirmative(
            input('Use user name "{}" in bevy "{}"'
                  '? [Y/n]:'.format(user_name, bevy)),
            default=True)  # stop looping if done

    if master:
        pub = None  # object to contain the user's ssh public key
        okay = 'n'
        user_home_pub = Path('/home') / user_name / '.ssh/authorized_keys'
        user_key_file = Path(USER_SSH_KEY_FILE_NAME.format(user_name))
        try:  # named user's default location on this machine?
            print('trying file: "{}"'.format(user_home_pub))
            pub = user_home_pub.open()
        except (OSError):
            try:  # Vagrant shared directory to user's home on host?
                user_home_pub = Path('/my_home') / '.ssh/authorized_keys'
                print('trying file: "{}"'.format(user_home_pub))
                pub = user_home_pub.open()
            except (OSError):
                try:  # maybe it is already in the /srv tree?
                    user_home_pub = user_key_file
                    print('trying file: "{}"'.format(user_home_pub))
                    pub = user_home_pub.open()
                except (OSError):
                    print('No ssh public key found. You will have to supply it the hard way...')
        if pub:
            pub_key = pub.read()
            okay = input(
                '{} exists, and contains:"{}"\n  Copy that to all minions? [y/N]:'.format(
                    user_home_pub, pub_key))

        while not affirmative(okay):
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
        if affirmative(okay):
            # user_key_file.parent.mkdir(parents=True, exist_ok=True) # only works for Python3.5+
            os.makedirs(str(user_key_file.parent), exist_ok=True)  # 3.4
            # 3.5 user_key_file.write_text(pub_key)
            with user_key_file.open('w') as f:  # 3.4
                f.write(pub_key)  # 3.4
    return bevy, user_name


def write_user_pillar_file(my_linux_user, bslpaswd):
    user_def_file_name = Path(USER_SETTINGS_PILLAR_FILE)

    # python 3.4
    os.makedirs(str(user_def_file_name.parent), exist_ok=True)
    # python 3.5
    # user_def_file_name.parent.mkdir(parents=True, exist_ok=True)

    with user_def_file_name.open('w') as f:
        this_file = Path(__file__).resolve()
        f.write('# this file was created by {}\n'.format(this_file))
        f.write('# and will probably be replaced very soon by Salt.\n')
        f.write("my_linux_user: {}\n".format(my_linux_user))
        f.write("my_linux_uid: ''\n")
        f.write("my_linux_gid: ''\n")
        if bslpaswd:
            f.write('linux_password_hash: "{}"\n'.format(bslpaswd))
            f.write('force_linux_user_password: true\n')
    print('File "{}" written.'.format(user_def_file_name))
    print()


def get_salt_master_id():
    cmd = "salt-call --local config.get master --out=json"
    print(cmd)
    try:
        out = subprocess.check_output(cmd, shell=True)
        master_id = json.loads(out.decode())['local']
    except subprocess.CalledProcessError:
        print("salt-call not answering ?!")
        master_id = "!!No answer from salt-call!!"
    return master_id[0] if isinstance(master_id, list) else master_id


def choose_master_address(host_name):
    default = ''
    choices = salt_call_json('network.ip_addrs')['local']
    print('This machine has the following IP addresses:')
    for addr in choices:
        print(' -', addr)
        if addr.startswith('10.'):
            default = addr
    try:
        ip_ = socket.getaddrinfo(host_name, 4506, type=socket.SOCK_STREAM)
        print('Its hostname translates to {}'.format(ip_[0][4]))
        default = host_name  # if we arrive here, a DNS record was found
        for ip1 in ip_[1:]:
            print(' - {}'.format(ip1[4]))
    except (socket.error, IndexError):
        pass
    while ...:
        resp = input("What url address for the master? [{}]:".format(default))
        choice = resp or default
        try:  # look up the address we have, and see if it appears good
            ip_ = socket.getaddrinfo(choice, 4506, type=socket.SOCK_STREAM)
            print("Okay, the bevy master's address is {}.".format(ip_[0][4]))
            return choice  # it looks good -- exit the loop
        except (socket.error, IndexError):
            print('"{}" is not a valid IPv4 address.'.format(choice))


if __name__ == '__main__':

    default_user = getpass.getuser()
    if default_user != 'root':
        print('You must run this command using "sudo".')
        exit(126)
    default_user = os.environ['SUDO_USER']

    print('This program can create either a bevy salt-master (and cloud-master),')
    print('or a simple workstation to join the bevy.')
    master = affirmative(input('Should this machine be the master? [y/N]:'))

    my_node = Path(os.path.dirname(os.path.abspath(__file__)))
    print('my_node', repr(my_node))  ###
    bevy_root_node = (my_node / '../bevy_srv').resolve()  # this dir is the Salt file_roots dir
    print('salt_root_node=', repr(bevy_root_node))  ###

    bevy_srv = Path('/bevy_srv')  # will be a link to our state files.
    # create a symlink from /bevy_srv to the bevy_srv directory in this repo.
    if not Path('/vagrant/bevy_srv').exists():  # special case: started by "vagrant up"
        if bevy_srv.exists():
            if not bevy_srv.is_symlink():
                raise RuntimeError('Unexpected situation: Path "{}" '
                                   'already exists and is not a symbolic link.'.format(bevy_srv))
            # 3.5 if not bevy_root_node.samefile(bevy_srv):
            if not os.path.samefile(str(bevy_root_node), str(bevy_srv)): # 3.4
                bevy_srv.unlink()
        try:
            bevy_srv.symlink_to(bevy_root_node)
        except FileExistsError:
            pass

    bevy, user_name = request_bevy_username_and_password(master)

    # check for use of virtualbox and Vagrant
    # test for Vagrant being already installed
    vagrant_present = subprocess.call('vagrant -v', shell=True) == 0

    cwd = runas = vagranthost = ''
    vbinst = False
    while ...:  # repeat until user says okay
        vbinst = False
        vagranthost = ''  # node ID of Vagrant host machine
        isvagranthost = affirmative(input(
            'Will this machine be a bevy host for Vagrant virtual machines? [y/N]:'))
        if isvagranthost:
            if master:
                vagranthost = 'bevymaster'
            else:
                vagranthost = platform.node().split('.')[0]
            vbinst = False if vagrant_present else affirmative(input(
                'Do you wish to install VirtualBox and Vagrant? [y/N]:'))
        elif master:
            print('What is/will be the node id of the Vagrant host machine?')
            vagranthost = input('(Leave blank if none.):')
            if vagranthost:
                try:
                    socket.inet_aton(vagranthost)  # an exception is expected
                    print('Please enter a node ID, not an IP address.')
                    continue  # user committed an entry error ... retry
                except OSError:
                    pass  # entry was not an IP address.  Good.
        if vagranthost:
            resp = input(
                'What user on {} will own the Vagrantbox files?'
                ' [{}]:'.format(vagranthost, user_name))
            runas = resp or user_name

            parent = os.path.abspath('..')
            resp = input(
                'What is the full path to the Vagrantfile on {}?'
                '[{}]:'.format(vagranthost, parent))
            cwd = resp or parent
            print()
            print('Using "{}" on node "{}"'.format(
                os.path.join(cwd, 'Vagrantfile'),
                vagranthost
            ))
            print('owned by {}.'.format(runas))
            if vagrant_present:
                print('Vagrant is already presesent on this machine.')
            else:
                print('VirtualBox and Vagrant {} be installed'.format(
                    'will' if vbinst else 'will not'))
        else:
            print('No Vagrant Box will be used.')
        if affirmative(input('Correct? [Y/n]:'), default=True):
            break

    bevymaster_name = BEVYMASTER_FQDN_PATTERN.format(bevy)

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

    try:  # forget a former master's key (if any)
        two = '2' if run_second_minion else ''
        Path('/etc/salt{}/pki/minion/minion_master.pub'.format(two)).unlink()
    except (FileNotFoundError, PermissionError):
        pass

    if master:
        # 3.5 bslpass = pwd_hash.hashpath.read_text().strip()
        with pwd_hash.hashpath.open() as f:  # 3.4
            bslpass = f.read().strip()  # 3.4
        write_user_pillar_file(user_name, bslpass)
        master_address = choose_master_address(bevymaster_name)
        print('\n\n. . . . . . . . . .\n')
        salt_state_apply('',  # blank name means: apply highstate
                         config_dir=str(my_node.resolve()),
                         bevy_root=str(bevy_root_node),
                         bevy=bevy,
                         node_name='bevymaster',
                         bevymaster_address=master_address,
                         run_second_minion=run_second_minion,
                         vbox_install=vbinst,
                         vagranthost=vagranthost,
                         runas=runas,
                         cwd=cwd,
                         doing_bootstrap=True,  # initialize environment
                         )

    else:  # not making a master, make a minion
        with pwd_hash.hashpath.open() as f:
            bslpass = f.read().strip()

        write_user_pillar_file(user_name, bslpass)

        if run_second_minion:
            bevymaster_address = bevymaster_name
        else:
            bevymaster_address = master_id
        while ...:  # loop until user says okay
            print('Trying {} for bevy master'.format(bevymaster_address))
            try:  # look up the address we have, and see if it appears good
                ip_ = socket.getaddrinfo(bevymaster_address, 4506, type=socket.SOCK_STREAM)
                okay = input('Use {} as your bevy master address? [y/N]:'.format(ip_[0][4]))
                if affirmative(okay):
                    break  # it looks good -- exit the loop
            except (socket.error, IndexError):
                pass  # looks bad -- ask for another
            bevymaster_address = input('Try again. Type the name or address of your bevy master?:')

        print('\n\n. . . . . . . . . .\n')
        node_name = platform.node().split('.')[0]  # your workstation's hostname
        salt_state_apply('configure_bevy_member',
                         config_dir=str(my_node.resolve()),
                         bevy_root=str(bevy_root_node),
                         bevy=bevy,
                         bevymaster_address=bevymaster_address,
                         node_name=node_name,
                         run_second_minion=run_second_minion,
                         vbox_install=vbinst,
                         my_linux_user=user_name,
                         vagranthost=vagranthost,
                         runas=runas,
                         cwd=cwd)
    print()
    print('{} done.'.format(__file__))
    print()