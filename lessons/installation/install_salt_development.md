### Installing a development copy of Salt

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
