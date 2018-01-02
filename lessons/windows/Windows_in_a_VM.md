#### Microsoft Windows ® in a Virtual Machine

The Vagrantfile in this directory specifies a Windows 10 ®
box supplied by Microsoft. It runs a trial version of win10
good for a few months.  

Click on your interactive VirtualBox GUI icon to start it.
You can use the GUI to monitor and modify your VM operation.

```bash
# typing on your VM Host machine
cd /projects/learn-salt/lessons/windows
vagrant up
```
If you see Windows starting in the GUI's `Preview` window,
but don't see a Windows GUI window on your screen, 
then click on the green right-arrow (➡) icon. You should be
rewarded with a new Windows desktop in a window on your display.

##### Loading Salt using your virtual Windows desktop.

You can use the GUI desktop on your Windows VM to install Salt on it.

- Click on the `e` icon to start your `Edge` browser.
- Go to https://docs.saltstack.com/en/latest/topics/installation/windows.html
(or search for `saltstack windows download`)
- download the appropriate installation package
- run the installer and agree to the license terms
- in `Master IP or Host Name` enter your Bevy Master IP address.
(for the demo bevymaster, use `172.17.2.2`.)
- in `Minion Name` enter your desired Salt Id. Perhaps `x-win10`.
- click the `Install` button.

After the smoke clears, go back to the Bevy Master and accept your new minion.

`sudo salt-key -a <Salt ID>`

For example: `sudo salt-key -a x-win10`

Proceed to send commands to your new Salt minion and its friends.

`sudo salt \* test.version`

`sudo salt x-win10 system.shutdown "Shutting down in five minutes" "5"`

##### Using salt-cloud to start Windows.

Salt-cloud can also be used to load and start Windows machines.
https://docs.saltstack.com/en/latest/topics/cloud/windows.html
