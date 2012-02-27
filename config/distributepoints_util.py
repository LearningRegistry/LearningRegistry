import os
import couchdb
import ConfigParser
import urllib2
import json	
import lrnodetemplate as t
from uuid import uuid4

scriptPath = os.path.dirname(os.path.abspath(__file__))
_PYLONS_CONFIG =  os.path.join(scriptPath, '..', 'LR', 'development.ini.orig')
_config = ConfigParser.ConfigParser()
_config.read(_PYLONS_CONFIG)


'''Default values read in from development.ini.orig'''
_DEFAULT_COUCHDB_URL = "http://localhost:5984/"
try:
    _DEFAULT_COUCHDB_URL = _config.get("app:main", "couchdb.url")
except Exception, e:
    print('Cannot find couchdb url from config file')

_NODE = "node"
try:
    _NODE = _config.get("app:main", "couchdb.db.node")
except Exception, e:
    print('Cannot find couchdb node from config file')

_DEFAULT_ENDPOINT = "http://localhost/"
try:
    _DEFAULT_ENDPOINT = _config.get("app:main", "node.endpoint.url")
except Exception, e:
    print('Cannot find node endpoint url from config file')


_NODE_DESCRIPTION = "node_description"

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
						print('\n'+str(e))
						print("Cannot delete specified connection\n")


		elif result == 'E' or result == 'e':
			flag = False
		else:
			continue
	
	return currentList	

'''Connect to CouchDB and retrieve wanted document'''
def getDocFromExistingCouchDB(dbName, couchdbURL=_DEFAULT_COUCHDB_URL, docID='', allDocs=False):
    resp = {}

    if allDocs:
        path = '/'.join([dbName,"_all_docs"])
    else:
        path = '/'.join([dbName, urllib2.quote(docID,'')])

    URI = couchdbURL + path
    try:
        req = urllib2.Request(URI)
        resp = json.loads(urllib2.urlopen(req).read())
    except Exception, e:
        print('Could not find requested document from couch: ' + URI)
       
    return resp	
	
'''Find all distribution connection documents'''	
def getExistingDistributionConnections(couchdbURL, dbName, nodeName, url=True):
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

    '''If there are no distribution connection documents, return an empty list, if you want the docs and not urls then it will return the docs'''    
    if not connDocList:
        return []
    elif connDocList and not url:
        return connDocList
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

'''Creates template for distribution endpoints, deletes any existing distribution connection docs'''
def publishNodeDistributionEndpoints(nodeUrl, server, dbname,  nodeName, connectionList):
    connection = dict(t.connection_description)
    connection['source_node_url']=nodeUrl

    '''Gather all existing connection docs'''
    existingConnDocs = getExistingDistributionConnections(_DEFAULT_COUCHDB_URL, dbname, nodeName, False)
    db = server[dbname]
    
    '''If they are not in the list then delete them'''
    for connDoc in existingConnDocs:
        if connDoc not in connectionList:
            try:
                del db[connDoc]
            except Exception, e:
                print('Could not delete ' +str(connDoc))

    '''Publish rest of list'''            
    for dest_node_url in connectionList:
        connection = dict(t.connection_description)
        connection['connection_id'] = uuid4().hex
        connection['source_node_url']=nodeUrl
        connection['destination_node_url'] = dest_node_url
        publishDistributionEndpointDoc(server, dbname, "{0}_to_{1}_connection".format(nodeName, dest_node_url), connection) 


def publishDistributionEndpointDoc(couchServer, dbname, name, doc_data):
    try:
        #delete existing document.
        db = couchServer[dbname]
        if "_rev" in doc_data:
            del doc_data["_rev"]

        try:
            del db[name]
        except:
            pass
        db[name] = doc_data
        print("Added config document '{0}' to '{1}'\n".format(name, dbname))
    except  Exception as ex:
        print("Exception when add config document:\n")
        exc_type, exc_value, exc_tb = sys.exc_info()
        pprint(traceback.format_exception(exc_type, exc_value, exc_tb))


if __name__ == "__main__":

	'''Create instance of couchdb server using existing url'''
	server =  couchdb.Server(_DEFAULT_COUCHDB_URL)
	existingNodeName = ""

	'''Retrieve node name'''
	try:
		node_desc = getDocFromExistingCouchDB(_NODE, _DEFAULT_COUCHDB_URL, _NODE_DESCRIPTION)
		existingNodeName = node_desc['node_name']
	except Exception, e:
		raise e
	
	'''Retrieve existing distribution targets, setup the new targets, publish the finalized list'''
	existingDistributionList = getExistingDistributionConnections(_DEFAULT_COUCHDB_URL, _NODE, existingNodeName)
	newDistributionList = setupDistributionConnections(existingDistributionList)
	publishNodeDistributionEndpoints(_DEFAULT_ENDPOINT, server, _NODE, existingNodeName, newDistributionList)
	