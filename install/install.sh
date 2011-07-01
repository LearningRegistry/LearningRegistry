#!/bin/bash
apt-get install python-pip
apt-get install nginx
pip install pylons
pip install flup
pip install pyparsing
pip install --upgrade couchdb
pip install restkit
pip install lxml
pip install iso8601plus
cp nginx.conf /etc/nginx/nginx.conf
