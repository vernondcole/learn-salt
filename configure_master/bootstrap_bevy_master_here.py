#!/usr/bin/env python3
# encoding: utf-8
# vim:softtabstop=4:ts=4:sw=4:expandtab:tw=120
"""A utility program to install a SaltStack minion, master and cloud controller
"""
import subprocess, os, getpass, json
from pathlib import Path
from urllib.request import urlopen

import pwd_hash

MINIMUM_SALT_VERSION = "2016.11.0"  # ... as a string... the month will be integerized below

# the path to the user definition file will change if two minions are running, hence the {}
FROM_BOOTSTRAP_FILE_NAME = '/etc/salt{}/minion.d/01_settings_from_bootstrap.conf'

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
           salt_root (or saltenv): a salt fileserver environment. Defaults to local_salt/salt if no --configdir.
           pillar_root (or pillarenv): a Pillar environment. Defaults to local_salt/pillar if no --configdir.
           localconfig: a minion configuration file to merge with the configuration environment values
           config_dir: a minion configuration environment.
    :return: None
    '''

    salt_root = kwargs.pop('salt_root', kwargs.pop('saltenv', None))  # also allow the SaltStack keyword
    pillar_root = kwargs.pop('pillar_root', kwargs.pop('pillarenv', None))
    config_dir = kwargs.pop('config_dir', None)
    localconfig = kwargs.pop('localconfig', None)

    cmdargs = {'salt_state': salt_state}
    parent = Path(__file__).parent.resolve()
    cmdargs['salt_root'] = '--file-root=%s' % salt_root if salt_root else  \
        "" if config_dir or localconfig else '--file-root={}'.format(parent / 'local_salt/salt')
    cmdargs['pillar_root'] = '--pillar-root=%s' % pillar_root if pillar_root else \
        "" if config_dir or localconfig else '--pillar-root={}'.format(parent / 'local_salt/pillar')
    cmdargs['config_dir'] = '--config-dir=%s' % config_dir if config_dir else ''
    cmdargs['localconfig'] = 'localconfig=%s' % localconfig if localconfig else ''

    cmdargs['pillar_data'] = 'pillar="%r"' % kwargs if kwargs else ''

    cmd = "salt-call --local state.apply %(salt_state)s --retcode-passthrough --state-output=mixed "\
          "%(salt_root)s %(pillar_root)s %(config_dir)s --log-file-level=info --log-level=critical " \
          "%(localconfig)s %(pillar_data)s " \
          % cmdargs

    print(cmd)
    ret = subprocess.call(cmd, shell=True)
    if ret == 0:
        print("Success")
    else:
        print('Error %d occurred while running Salt state "%s"'% (ret,
               salt_state if salt_state else "highstate"))


def salt_minion_version():
    try:
        out = subprocess.check_output("salt-call --version", shell=True)
        out = out.decode()
        version = out.split(" ")[1].split('.')
        version[1] = int(version[1])
    except subprocess.CalledProcessError:
        print("salt-minion not installed")
        version = ["",0,'']
    return version


def salt_install():
    print("Checking Salt Version")
    _current_salt_version = salt_minion_version()
    if _current_salt_version >= minimum_salt_version:
        print("Success: %s" % _current_salt_version)
    else:
        _salt_install_script = "/tmp/bootstrap-salt.sh"
        print("Downloading Salt Bootstrap to %s" % _salt_install_script)
        with open(_salt_install_script, "w+") as f:
            f.write(urlopen("http://bootstrap.saltstack.com/stable/bootstrap-salt.sh").read().decode())
        print("Success")
        print("Bootstrapping Salt")
        try:
            print("sh %s -X stable" % (_salt_install_script))
            subprocess.call("sudo sh %s -X -M -L -P stable" % (_salt_install_script), shell=True)
            print("Salt Installed")
        except OSError as ex:
            print(ex)
            raise ex
        return True   # flag that we installed Salt

def request_bevy_username_and_password(bevy_srv):
    """ get user's information so that we can build a user for her on each minion
    
    :param bevy_srv: a pathlib.Path of the top of the bevy master tree
    """
    loop = NotImplemented   # Python trivia: NotImplemented evaluates as True
    while loop:
        print()
        bevy = input("Name your bevy: {'bevy1'}:") or 'bevy1'
        print()

        print('Please supply your desired user name to be created on all minions.')
        print('(Hit <enter> to use "{}")'.format(default_user))
        user_name = input('User Name:') or default_user
        print()
        if pwd_hash.hashpath.exists() and loop is NotImplemented:
            print('(using the password hash from {}'.format(pwd_hash.hashpath))
        else:
            pwd_hash.make_file()
            pwd_hash.hashpath.chmod(0o666)
        loop = not \
            input('Use this user name and password in bevy "{}"'
                  '?'.format(bevy)).lower().startswith('y')

    pub = None  # object to contain the user's ssh public key
    okay = ''
    user_home_pub = Path('/home') / user_name / '.ssh/authorized_keys'
    user_key_file = Path(USER_SSH_KEY_FILE_NAME.format(user_name))
    try:
        print('trying file: "{}"'.format(user_home_pub))
        pub = user_home_pub.read_text()
    except (OSError):
        try:   # Vagrantfile map to user's home on host
            user_home_pub = Path('/my_home') / '.ssh/authorized_keys'
            print('trying file: "{}"'.format(user_home_pub))
            pub = user_home_pub.read_text()
        except (OSError):
            try:  # maybe it is already there?
                user_home_pub = user_key_file
                print('trying file: "{}"'.format(user_home_pub))
                pub = user_home_pub.read_text()
            except (OSError):
                print('No ssh public key found. You will have to supply it the hard way...')
    if pub:
        okay = input(
            '{} exists, and contains:"{}"\n  Copy that to all minions?'.format(
                user_home_pub, pub))

    while not okay.lower().startswith('y'):
        print('Next, cut the text of your ssh public key to transmit it\n')
        print('to your new server.\n')
        print('You can usually get it by typing:\n')
        print('   cat ~/.ssh/id_rsa.pub\n')
        print()
        pub = input('Paste it here --->')
        print()
        print('I received:{}\n'.format(pub))
        okay = input("Use that? ('exit' to bypass ssh keys):")
        if okay.lower().startswith('y') or okay.lower() == 'exit':
            break
    if okay.lower().startswith('y'):
        user_key_file.parent.mkdir(parents=True, exist_ok=True) # only works for Python3.5+
        user_key_file.write_text(pub)
    return bevy, user_name, vbinst

def write_user_pillar_file(my_linux_user, bslpaswd):
    user_def_file_name = Path('/srv/pillar/my_user_settings.sls')
    user_def_file_name.parent.mkdir(parents=True, exist_ok=True)
    with user_def_file_name.open('w') as f:
        this_file = Path(__file__).resolve()
        f.write('# this file was created by {}\n'.format(this_file))
        f.write('#\n')
        f.write("my_linux_user: {}\n".format(my_linux_user))
        f.write('#\n')
        f.write("my_linux_uid: ''\n")
        f.write("my_linux_gid: ''\n")
        f.write('#\n')
        f.write('linux_password_hash: "{}"\n'.format(bslpaswd))
        f.write('force_linux_user_password: true\n')
    print('File "{}" written.'.format(user_def_file_name))
    print()


def get_salt_master_id():
    try:
        out = subprocess.check_output("salt-call --local grains.get master --out=json", shell=True)
        master_id = json.loads(out.decode())['local']
    except subprocess.CalledProcessError:
        print("salt-call not answering ?!")
        master_id = "!!No answer from minion!!"
    print('Your Salt master was detected as "{}"'.format(master_id))
    return master_id[0] if isinstance(master_id, list) else master_id

if __name__ == '__main__':

    default_user = getpass.getuser()
    if default_user != 'root':
        print('You must run this command using "sudo".')
        exit(126)
    default_user = os.environ['SUDO_USER']

    salt_root_node = Path(os.path.abspath('../bevy_srv'))  # this dir is the Salt file_roots dir
    bevy_srv = Path('/bevy_srv')
    # create a symlink from /bevy_srv to the bevy_srv directory in this repo.
    if not Path('/vagrant/bevy_srv').exists():  # special case: started by "vagrant up"
        if bevy_srv.exists():
            if not bevy_srv.is_symlink():
                raise RuntimeError('Unexpected situation: Path "{}" '
                      'already exists and is not a symbolic link.'.format(bevy_srv))
            if not salt_root_node.samefile(bevy_srv):
               bevy_srv.unlink()
        try:
            bevy_srv.symlink_to(salt_root_node)
        except FileExistsError:
            pass

    bevy, user_name, vbinst = request_bevy_username_and_password(bevy_srv)

    bevymaster_name = BEVYMASTER_FQDN_PATTERN.format(bevy)

    we_installed_it = salt_install()

    if we_installed_it:
        run_second_minion = False
    else:
        master_id = get_salt_master_id()
        if master_id.startswith('!'):
            raise ValueError('Something wrong. Salt master should be known at this point.')
        run_second_minion = master_id not in ['localhost', 'salt', '127.0.0.1']

    bslpass = pwd_hash.hashpath.read_text().strip()


    write_user_pillar_file(user_name, bslpass)

    my_node = Path(os.path.dirname(__file__))
    salt_state_apply('',  # blank name means: apply highstate
                     config_dir=my_node.resolve(),
                     bevy=bevy,
                     bevymaster_name=bevymaster_name,
                     run_second_minion=run_second_minion,
                     vbox_install=vbinst)
    print()
    print('{} done.'.format(__file__))
    print()
