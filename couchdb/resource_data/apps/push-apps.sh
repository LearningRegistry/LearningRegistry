#!/bin/bash

#SERVER=http://192.168.96.129:5984
SERVER=http://127.0.0.1:5984

. ~/virtualenv/lr27/bin/activate

couchapp push oai-pmh ${SERVER}/resource_data
couchapp push learningregistry ${SERVER}/resource_data
couchapp push filter ${SERVER}/resource_data
