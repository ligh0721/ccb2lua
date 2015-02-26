#!/usr/bin/env sh

curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
chmod +x get-pip.py
sudo ./get-pip.py
sudo pip install mako biplist
