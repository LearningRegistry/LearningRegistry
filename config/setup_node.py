#!/usr/bin/env python
#    Copyright 2011 Lockheed Martin
#

#
#Simple script to setup and initialize a learning registry node documents and
# commit to a specified coudbserver.
#

import ConfigParser
import os
import couchdb
import urlparse
import subprocess
import lrnodetemplate as t
from uuid import uuid4
import shutil

from setup_utils import *

scriptPath = os.path.dirname(os.path.abspath(__file__))

_PYLONS_CONFIG_SRC =  os.path.join(scriptPath, '../LR/development.ini.orig')
_PYLONS_CONFIG_DEST = os.path.join(scriptPath, '../LR/development.ini')
_COUCHAPP_PATH = os.path.join(scriptPath, '../couchdb/apps')

# add path to virtualenv if the environment variable is set
if os.getenv('VIRTUAL_ENV') is not None:
    _VIRTUAL_ENV_PATH = os.path.expandvars('${VIRTUAL_ENV}')
else:
    _VIRTUAL_ENV_PATH = ''

print ("\n{0}\n{1}\n{2}".format(
                _PYLONS_CONFIG_SRC, _PYLONS_CONFIG_DEST, _COUCHAPP_PATH))

#Read the pylons configuration to get the database names.
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG_SRC)

_RESOURCE_DATA = _config.get("app:main", "couchdb.db.resourcedata")
_NODE = _config.get("app:main", "couchdb.db.node")
_COMMUNITY = _config.get("app:main", "couchdb.db.community")
_NETWORK = _config.get("app:main", "couchdb.db.network")

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
    for service_type in ['access', 'broker', 'publish', 'administrative', 'distribute', 'oaipmh', 'harvest']:
        try:
            plugin = __import__("services.%s" % service_type, fromlist=["install"])
            plugin.install(server, _NODE, nodeSetup)
        except Exception as e:
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
        command = os.path.join(
            _VIRTUAL_ENV_PATH, 'bin', 'couchapp') + " push {0} {1}".format(
                os.path.join(_COUCHAPP_PATH, app), resourceDataUrl
                )
        print("\n{0}\n".format(command))
        p = subprocess.Popen(command, shell=True)
        p.wait()
    print("\n\n\n")
