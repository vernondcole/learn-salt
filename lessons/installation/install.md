## Software installation

#### MarkDown Viewer

Some of the lesson material in this project (especially the home index)
is in MarkDown format.  The GitHub web site automatically converts MarkDown
(.md) files to html, so that you can read them in your browser.

When you download the project to your own workstation, you will not have that help.
You will want to load an addon to your browser.  

For [Firefox]() use 
[MarkDown Viewer](https://addons.mozilla.org/en-US/firefox/addon/markdown-viewer/)

For [Chrome](https://www.google.com/chrome/) try
[MarkDown Viewer](https://chrome.google.com/webstore/detail/markdown-viewer/ckkdlimhmcjmikdlpkmbgfkaikojcbjk?utm_source=chrome-app-launcher-info-dialog)

To install a native MarkDown reader/editor on your workstation, try
[ReText](https://github.com/retext-project/retext).

#### Salt (development version)

- install git

- install [Python3](http://python.org)

  - Windows & MacOS install from [the official download page](https://www.python.org/downloads/)

  - Linux (Debian & Raspbian) `sudo apt install python3`

  - Ubuntu (since 16.04) Python3 is already installed as the system default.

- clone the salt git repository

	```
	cd /projects
	git clone git@github.com:saltstack/salt.git
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
  notepad++ salt-call.bat
  ```

  - create .bat files for salt-call, salt-minion, and notepad++
  
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
  
  ```
  # file edit.bat
  notepad++ %*
  ```
  
  - Add C:\utils to your system PATH.  If there is an entry for `C:\salt` make sure `\utils` is searched first.
  

	