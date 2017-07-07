#!/usr/bin/env python3
try:
    import passlib.hash as ph  # must use passlib module on Mac OS-x systems.
    sha = ph.sha512_crypt
    import random
except ImportError:
    sha = None
    import crypt  # can use built-in crypt on Linux

import getpass
from pathlib import Path

HASHFILE_NAME = 'bevy_linux_password.hash'
hashpath = Path.home() / '.ssh' / HASHFILE_NAME


def make_file():
    # TODO: add the capability to set Salt sdb://salt-cloud-keystore/password
    dashline = 78 * '-'
    print(dashline)
    print()
    print('This program will request a password, and send its Linux "Hash" to...')
    print(' {}'.format(hashpath))
    print()

    while True:
        pw1 = getpass.getpass()
        pw2 = getpass.getpass("And again: ")

        if pw1 != pw2:
            print("Passwords didn't match")
            continue
        else:
            if sha is None:
                pwhash = crypt.crypt(pw1)
            else:
                pwhash = sha.hash(pw1, salt=hex(random.getrandbits(64))[2:], rounds=5000) # 5000 is magic, do not change
            print('the hash is...')
            print(pwhash)
        if 0 < len(pwhash) < 32:
            print('Note: the crypt module is fully implemented only on Linux Python3.')
            print('  Your hash is too small to be SHA-2, meaning it will not work for a SaltStack user definition.')
            print('  You need to "pip3 install passlib"')
        if (input("Use this password hash? (y/n)[y]:") or 'y').lower().startswith('y'):
            break

    with hashpath.open('w') as pf:
        pf.write(pwhash + '\n')
    print('File {} written.'.format(hashpath))
    print(dashline)

if __name__ == "__main__":
    make_file()
