Windows users typically use the program `PuTTY`
for ssh connections. PuTTY has its own unique way
of storing ssh key information.

Vagrant (and most other POSIX style systems) expect
to find ssh keys in POSX format and default location.

That is to say, your private key file will be in
`<your home directory>/.ssh/id_rsa` and your public
key will be in `<your home directory>/.ssh/id_rsa.pub`.

PuTTY users need to run PuTTYgen to export their
private key file to `C:\Users\<your user name>\.ssh\id_rsa`
and save a copy of their public key in `C:\Users\<your user name>\.ssh\id_rsa.pub`.

In particular, you need to do this before running `vagrant ssh` commands.
