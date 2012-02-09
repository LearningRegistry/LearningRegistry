#import setup_utils as su
from setup_utils import getDocFromExistingCouchDB
from setup_node import publishNodeConnections
import os
import couchdb
import ConfigParser
	
'''Prompt user through list of distribution points'''
def setupDistributionConnections(currentList):
	
	newList = []

	'''Prompt to add or remove points'''
	flag = True
	while flag:
		print("\nCurrent distribution connections:")
		if len(currentList) > 0:
			for item in currentList:
				print item + '\n'
		else:
			print("No distribution connections")		

		result = raw_input("\n[A]dd, [R]emove connections, [E]xit: ")

		if result == 'A' or result == 'a':
			for item in currentList:
				print item

			'''Get input from user, split into different targets and add to existing distribution list'''	
			inputTargets = raw_input("Please enter any distrubtion targets you would like to add separated by a space: ")

			if inputTargets:
				newList = inputTargets.split(' ')

				for item in newList:
					currentList.append(item)
			
		elif result == 'R' or result == 'r':
			if not len(currentList) > 0:
				print("\nThere are no distribution targets to remove\n")
			else:	
				for index, item in enumerate(currentList):
					print '[' + str(index) +'] ' + item

				'''Get user input on which points to remove from the list'''	
				inputTarget = raw_input("Please enter the corresponding number to remove the distribution target:")
			
				if inputTarget:
					try:
						del currentList[int(inputTarget)]
					except Exception, e:
						print('\n'+e)
						print("Cannot delete specified connection\n")

		elif result == 'E' or result == 'e':
			flag = False
		else:
			continue
	
	return currentList	
	
'''Find all distribution connection documents'''	
def getExistingDistrubutionConnections(couchdbURL, dbName, nodeName):
    '''Create filter to find distribution connection docs'''
    connFilter = nodeName + "_to_"
    connDocList = []

    '''Grab all docs from database and only grab those that contain the filter'''
    try:
        connDocs = getDocFromExistingCouchDB(dbName, couchdbURL,allDocs=True)
        
        for connDoc in connDocs['rows']:
            if connFilter in connDoc['id']:
                connDocList.append(connDoc['id'])

    except Exception, e:
        print(e)
        print('Connection to Node database not established, using default distribution connections')        

    '''If there are no distribution connection documents, return an empty list'''    
    if not connDocList:
        return []
    else:    
        return getExistingDistrubtionURLs(couchdbURL, dbName, connDocList)    

'''Fetch the distribution URLs from each distribution connection doc'''
def getExistingDistrubtionURLs(couchdbURL, dbName, connDocList):
    connUrlList = []

    '''For each distribution connection doc, retrieve and append the destination_node_url to the list and return it'''
    for connDoc in connDocList:
        try:
            connURL = getDocFromExistingCouchDB(dbName, couchdbURL, connDoc)
            connUrlList.append(connURL['destination_node_url'])

        except Exception, e:
            print(e)
            print('Connection to Node database not established, using default distribution connection URLs')

    return connUrlList



if __name__ == "__main__":
	

	scriptPath = os.path.dirname(os.path.abspath(__file__))
	_PYLONS_CONFIG =  os.path.join(scriptPath, '..', 'LR', 'development.ini.orig')
	_config = ConfigParser.ConfigParser()
	_config.read(_PYLONS_CONFIG)

	_DEFAULT_COUCHDB_URL = _config.get("app:main", "couchdb.url")
	_NODE = _config.get("app:main", "couchdb.db.node")
	_NODE_DESCRIPTION = "node_description"
	_DEFAULT_ENDPOINT = _config.get("app:main", "node.endpoint.url")


	server =  couchdb.Server(_DEFAULT_COUCHDB_URL)
	existingNodeName = ""

	try:
		node_desc = getDocFromExistingCouchDB(_NODE, _DEFAULT_COUCHDB_URL, _NODE_DESCRIPTION)
		existingNodeName = node_desc['node_name']
	except Exception, e:
		raise e
	
	existingDistributionList = getExistingDistrubutionConnections(_DEFAULT_COUCHDB_URL, _NODE, existingNodeName)
	newDistributionList = setupDistributionConnections(existingDistributionList)
	publishNodeConnections(_DEFAULT_ENDPOINT, server, _NODE, existingNodeName, newDistributionList)
	