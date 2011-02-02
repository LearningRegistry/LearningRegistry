#!/bin/bash
apt-get install python-pip
apt-get install lighttpd
pip install pylons
pip install flup
pip install --upgrade couchdb 
cp lighttpd.conf /etc/lighttpd/lighttpd.conf
