## Software installation

_**Remember: Before editing any files in any project,
switch to a new branch in `git`.**_

```
git branch my_edits
git checkout my_edits
```
now ... on to what you really came here for ...

#### MarkDown Viewer

Some of the lesson material in this project (especially the home index)
is in [MarkDown](http://commonmark.org/) format.  The GitHub web site automatically converts MarkDown
(.md) files to html, so that you can read them in your browser within GitHub.

But, you will be downloading the repository to your workstation anyway, and it
makes sense to use your local copy of the lessons.
On your workstation, you will not have the advantage of the GitHub magic, so
you will want to load an addon to your browser to display .md files prettily.


For [Firefox]() try
[MarkDown Viewer](https://addons.mozilla.org/en-US/firefox/addon/markdown-viewer/).

For [Chrome](https://www.google.com/chrome/) try
[this MarkDown Viewer](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk?utm_source=chrome-app-launcher-info-dialog)

To install a native MarkDown reader/editor on your workstation, try
[ReText](https://github.com/retext-project/retext).

#### Salt (after Salt Oxygen is released)

- Linux (and other POSIX systems)
    ```(bash)
    wget  -O bootstrap-salt.sh https://bootstrap.saltstack.com
    # that ^ is a capitol "Oh" not a zero
    sudo sh bootstrap-salt.sh 
    ```

- Everything else

    [See the official Salt page](https://docs.saltstack.com/en/latest/topics/installation/index.html#quick-install)

#### Salt (Oxygen development version, run time)

- linux (running system, no source code remaining)
    ```(bash)
    wget  -O bootstrap-salt.sh https://bootstrap.saltstack.com
    # that ^ is a capitol "Oh" not a zero
    sudo sh bootstrap-salt.sh git
    ```

- others

    do the full install-from-source below

#### Salt (development copy of source)

\[[also see the instructions in the Salt docs](https://docs.saltstack.com/en/latest/topics/development/hacking.html)\]

- install git

- install [Python3](http://python.org)

  - Windows & MacOS install from [the official download page](https://www.python.org/downloads/)

  - Linux (Debian & Raspbian) `sudo apt install python3`

  - Ubuntu (since 16.04) Python3 is already installed as the system default.

- clone the salt git repository

	```
	cd /projects
	git clone --depth 1 git@github.com:saltstack/salt.git
	cd salt
	```

- install Salt

  - Linux 
  ```
  sudo pip3 install -r requirements/dev_python34.txt
  sudo python3 setup.py install
  ```
  
  - Windows
  
      - install [notepad++](https://notepad-plus-plus.org/download/)
      
      ```
      py -m pip3 install -r requirements/dev_python34.txt
      py setup.py install
      cd %LOCALAPPDATA%\programs\python\python36\scripts
      copy salt-call salt-call.py
      copy salt-minion salt-minion.py
      ```
    
      - create a directory for utility programs
      
          (or you could use an existing directory in the search path.)
        
          ```
            mkdir c:\utils
            cd \utils
          ```  
      
      - Add C:\utils to your system PATH.
        
        If there is an entry for `C:\salt` make sure `c:\utils` is searched first.
        
        (or same idea for for existing directory.)
    
      - create .bat files for salt-call, salt-minion, and notepad++, in your utils directory.
      
      ```
      # file edit.bat
      notepad++ %*
      ```
        
      ```
      # file salt-call.bat
      py %localappdata%\programs\python\python36\scripts\salt-call %*
      ```
    
      ```
      # file salt-cp.bat
      py %localappdata%\programs\python\python36\scripts\salt-cp %*
      ```
    
      ```
      # file salt-minion.bat
      py %localappdata%\programs\python\python36\scripts\salt-minion %*
      ```
