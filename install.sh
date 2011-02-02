#!/bin/bash
apt-get install python-pip
apt-get install git
pip install pylons
pip install flup
pip install --upgrade couchdb 
git clone git://github.com/LearningRegistry/LearningRegistry.git
cp LearningRegistry/lighttpd.conf /etc/lighttpd/lighttpd.conf