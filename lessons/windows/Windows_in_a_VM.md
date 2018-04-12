#### Microsoft Windows ® in a Virtual Machine

The big Vagrantfile defines three Windows® machines.
`win10` is a Windows 10® which runs a trial version of win10
good for a few months.  

You can use the interactive VirtualBox GUI icon to monitor and modify your VM operation.

```bash
# typing on your VM Host machine
cd /projects/learn-salt
vagrant up win10
```

If you see Windows starting in the GUI's `Preview` window,
but don't see a Windows GUI window on your screen, 
then click on the green right-arrow (➡) icon. You should be
rewarded with a new Windows desktop in a window on your display.

- Click on the File Explorer `folder` icon on the bottom control bar.
- Click on the `Network` icon.
- Click on the yellow bar near the top, and request that your network be 
enabled as a private network.
- Click on the `Network` icon.
- after a while, you will see a network node named "VBOXSVR"
- click on "VBOXSVR"

Congratulations! You have located the VirtualBox shared directory.
The contents of this virtual directory are actually on your host computer disk.

- click on the `Salt install Windows shortcut` icon and you can skip the first 
two steps below.
 

##### Using salt-cloud to start Windows.

Salt-cloud can also be used to load and start Windows machines.
https://docs.saltstack.com/en/latest/topics/cloud/windows.html

##### Running a Microsoft Compiler

It is still possible to find a Microsoft C++ or C# compiler which can be used for free. 
If you are working on an open source project, you can run the Community Edition
of Visual Studio. It is also possible to download only the tools you need to build
a project using only command-line tools (like you want to do on a build server)
if you look carefully near the bottom of the selections in 
https://www.visualstudio.com/downloads
to find `Build Tools for Visual Studio 2017`. 

Instructions to use the command-line tools can be found in 
https://docs.microsoft.com/en-us/cpp/build/building-on-the-command-line.

##### or try a VirtualBox image with Visual Studio pre-installed.

Not managed by Vagrant, but easy enough to use from the VirtualBox GUI,
https://developer.microsoft.com/en-us/windows/downloads/virtual-machines 
features a time-limited copy of Windows 10 with Visual Studio 2017.

If you use this arrangement, you will not be able to use ssh connections
(to github.com for example) because your VM will not be known (will not
have a public key) on target servers. You will need to copy your
private ssh key (`~/.ssh/id_rsa`) to 'C:\Users\User\.ssh`. 

It may be most convenient to use the VirtualBox GUI to create a shared
directory of your host's user home. You can find it on the VM's 'VBOXSVR' share.
You can copy your private key, or git can clone
a repo, from that share, 
or you can open your project there with Visual Studio.
