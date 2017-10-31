#!/usr/bin/env bash -x
if ! type "brew" > /dev/null; then
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)";
fi
brew cask install vagrant;
brew cask install virtualbox;
pushd
cd ../../
if ! "salt-call --version"; then
  git clone -b cloud-vagrant-driver --single-branch https://github.com/vernondcole/salt.git
  cd salt
  git checkout --track -b origin/cloud-vagrant-driver
  git pull
  pip3 install -r requirements/base.txt
  pip3 install -r requirements/zeromq.txt
  pip3 install -r requirements/dev_python34.txt
  python3 setup.py install
fi
popd
