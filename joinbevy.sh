#!/bin/bash
set -x
pushd configure_machine
/usr/bin/python3 bootstrap_bevy_member_here.py
popd
