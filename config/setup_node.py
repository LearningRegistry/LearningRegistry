#!/usr/bin/env python
#    Copyright 2011 Lockheed Martin
#

#
#Simple script to setup and initialize a learning registry node documents and
# commit to a specified coudbserver.
#

import ConfigParser, os
import couchdb
import sys
import json
import traceback
import urlparse
import subprocess
from pprint import pprint
import lrnodetemplate as t
from uuid import uuid4
import shutil

scriptPath = os.path.dirname(os.path.abspath(__file__))

_PYLONS_CONFIG_SRC =  os.path.join(scriptPath, '../LR/development.ini.orig')
_PYLONS_CONFIG_DEST = os.path.join(scriptPath, '../LR/development.ini')
_COUCHAPP_PATH = os.path.join(scriptPath, '../couchdb/apps')

print ("\n{0}\n{1}\n{2}".format(
                _PYLONS_CONFIG_SRC, _PYLONS_CONFIG_DEST, _COUCHAPP_PATH))

#Read the pylons configuration to get the database names.
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG_SRC)

_RESOURCE_DATA = _config.get("app:main", "couchdb.db.resourcedata")
_NODE = _config.get("app:main", "couchdb.db.node")
_COMMUNITY = _config.get("app:main", "couchdb.db.community")
_NETWORK = _config.get("app:main", "couchdb.db.network")

#Default url to the couchdb server.
_DEFAULT_COUCHDB_URL =  "http://localhost:5984/"


def CreateDB(couchServer = _DEFAULT_COUCHDB_URL,  dblist=[], deleteDB=False):
    '''Creates a DB in Couch based upon config'''
    for db in dblist:
        if deleteDB:
            try:
                del couchServer[db]
            except couchdb.http.ResourceNotFound as rnf:
                print("DB '{0}' doesn't exist on '{1}', creating".format(db, couchServer))
        else:
            try:
                existingDB = couchServer[db]
                print("Using existing DB '{0}' on '{1}'\n".format(db, couchServer))
                continue
            except:
                pass
        try:
            couchServer.create(db)
            print("Created DB '{0}' on '{1}'\n".format(db, couchServer))
        except Exception as e:
            print("Exception while creating database: {0}\n".format(e) )


def PublishDoc(couchServer, dbname, name, doc_data):
    
    try:
        db = couchServer[dbname]
        #delete existing document.
        try:
            del db[name]
        except:
            pass
        db[name] = doc_data
        print("Added config document '{0}' to '{1}".format(name, dbname))
    except  Exception as ex:
        print("Exception when add config document:\n")
        exc_type, exc_value, exc_tb = sys.exc_info()
        pprint(traceback.format_exception(exc_type, exc_value, exc_tb))
   

def testCouchServer(serverURL):
    try:
        couchServer =  couchdb.Server(url=serverURL)
        # Try to get the server configuration to ensure the the server is up and
        # and running. There may be a better way of doing that.
        couchServer.config()
    except Exception as e:
        print(e)
        print("Cannot connect to couchDB server '{0}'\n".format(serverURL))
        return False
    return True

def getInput(question, defaultInput=None,  validateFunc=None):
    ques = question+':  '
    if defaultInput is not None:
            ques = question+' [{0}]:  '.format(defaultInput)

    while True:
        userInput = raw_input(ques)
        inputLen =  len(userInput.strip())
        if inputLen == 0:
            if defaultInput is not None:
                userInput = defaultInput
            else:
                continue

        if validateFunc is not None and validateFunc(userInput) == False:
            continue

        return userInput


def getSetupInfo():
    """Get the user node info"""
    nodeSetup = {}
    couchDBUrl  = getInput("Enter your couchDB server URL",
                                            None, testCouchServer)

    nodeSetup['couchDBUrl'] = couchDBUrl

    nodeName = getInput("Enter your node name", "Node@{0}".format(couchDBUrl))
    nodeSetup['node_name'] = nodeName

    nodeDescription = getInput("Enter your node description", nodeName)
    nodeSetup['node_description'] = nodeDescription

    adminUrl = getInput("Enter node admin indentity",
                                    "{0}.node.admin@learningregistry.org".format(couchDBUrl))
    nodeSetup['node_admin_identity'] = adminUrl

    distributeTargets = getInput("Enter the URLs of nodes that you wish to distribute to",
                                                 "")
    nodeSetup['connections'] = distributeTargets.split()

    isNodeOpen = getInput('Is the  node "open" (T/F)', 'T')
    nodeSetup['open_connect_source']  = (isNodeOpen=='T')

    isDistributeDest = getInput("Does the node want to be the destination for replication (T/F)", 'T')
    nodeSetup['open_connect_dest'] =(isDistributeDest =='T')
    return nodeSetup


if __name__ == "__main__":

    from optparse import OptionParser
    import os

    parser = OptionParser()
    parser.add_option("-d", "--devel", dest="devel", action="store_true", default=False,
                      help="Development mode allows the setting of network and community.",
                    )
    (options, args) = parser.parse_args()
    print("\n\n=========================\nNode Configuration\n")
    if options.devel:
        community = getInput("Enter the community id")
        t.community_description['community_id'] = community
        t.community_description['community_name'] = community
        t.community_description['community_description'] = community
        t.network_description['community_id'] = community
        t.node_description['community_id'] = community

        network = getInput("Enter the network id")
        t.network_description['network_id'] = network
        t.network_description['network_name'] = network
        t.network_description['network_description'] = network
        t.node_description['network_id'] = network
        t.network_policy_description['network_id'] = network
        t.network_policy_description['policy_id'] =network+" policy"




    nodeSetup = getSetupInfo()
    print("\n\n=========================\nNode Configuration\n")
    for k in nodeSetup.keys():
        print("{0}:  {1}".format(k, nodeSetup[k]))

    #create a copy of the existing config file as to not overide it.
    if os.path.exists(_PYLONS_CONFIG_DEST):
        backup = _PYLONS_CONFIG_DEST+".backup"
        print("\nMove existing {0} to {1}".format(_PYLONS_CONFIG_DEST, backup))
        shutil.copyfile(_PYLONS_CONFIG_DEST, backup)
        
    #Update pylons config file to use the couchdb url
    _config.set("app:main", "couchdb.url", nodeSetup['couchDBUrl'])
    destConfigfile = open(_PYLONS_CONFIG_DEST, 'w')
    _config.write(destConfigfile)
    destConfigfile.close()

    server =  couchdb.Server(url= nodeSetup['couchDBUrl'])

    #Create the databases.
    CreateDB(server, dblist=[_RESOURCE_DATA])
    #Delete the existing databases
    CreateDB(server, dblist=[ _NODE, _NETWORK, _COMMUNITY], deleteDB=True)

    #Add the network and community description
    PublishDoc(server, _COMMUNITY, "community_description", t.community_description)
    PublishDoc(server, _NETWORK,  "network_description", t.network_description)
    policy = {}
    policy.update(t.network_policy_description)
    PublishDoc(server, _NETWORK,'network_policy_description', policy)


    #Add node description
    node_description = {}
    node_description.update(t.node_description)
    node_description['node_name'] = nodeSetup['node_name']
    node_description['node_description'] = nodeSetup['node_description']
    node_description['node_admin_identity'] = nodeSetup['node_admin_identity']
    node_description["open_connect_source"] = nodeSetup["open_connect_source"]
    node_description["open_connect_dest"] = nodeSetup["open_connect_dest"]
    node_description['node_id'] = uuid4().hex
    PublishDoc(server, _NODE, 'node_description', node_description)

    for dest_node_url in nodeSetup['connections']:
        connection = {}
        connection.update(t.connection_description)
        connection['connection_id'] = uuid4().hex
        connection['source_node_url']=nodeSetup['couchDBUrl']
        connection['destination_node_url'] = dest_node_url
        PublishDoc(server, _NODE, "{0}_to_{1}_connection".format(
                                                nodeSetup['node_name'], dest_node_url), connection)


    #Install the services, by default all the services are installed.
    for service_type in ['access', 'broker', 'publish', 'administrative', 'distribute']:
        service = {}
        service.update(t.service_description)
        service['service_type'] =service_type
        service['service_id'] = uuid4().hex
        service['service_name'] = service_type + " service"
        service['service_description']= service_type + " service"
        PublishDoc(server, _NODE, service_type + " service", service)
        
    #Push the couch apps
    #Commands to go the couchapp directory and push all the apps.
    print("\n============================\n")
    print("Pushing couch apps ...")
    resourceDataUrl = urlparse.urljoin( nodeSetup['couchDBUrl'], _RESOURCE_DATA)
    for app in os.listdir(_COUCHAPP_PATH):
        command = "/home/wegrata/virtualenv/lr/bin/couchapp push {0} {1}".format(
                            os.path.join(_COUCHAPP_PATH, app), resourceDataUrl)
        print("\n{0}\n".format(command))
        p = subprocess.Popen(command, shell=True)
        p.wait()
    print("\n\n\n")
