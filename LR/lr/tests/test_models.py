from pylons import config
import urllib2
import couchdb
import json
from lr.model.resource_data_monitor import IncomingCopyHandler,CompactionHandler,UpdateViewsHandler
from lr.util.decorators import PublishTestDocs
from lr.util.testdata import getTestDataForMetadataFormats
import copy
import logging
import uuid
from unittest import TestCase
import threading
import time
_DEFAULT_CHANGE_OPTIONS = {'feed': 'continuous',
                           'include_docs':True}
log = logging.getLogger(__name__)                           
def get_design_docs(db):
	return db.view('_all_docs',include_docs=True,
                                                startkey='_design%2F',endkey='_design0')	
def load_data():
	s = couchdb.Server(config['couchdb.url'])
	node = s[config['couchdb.db.node']]
	node_description = node['node_description']
	with open('lr/tests/data/nsdl_dc/data-000000000.json','r') as f:
		data = json.load(f)	
	for doc in data['documents']:
		doc['publishing_node'] = node_description['node_id']
		doc['doc_ID'] = uuid.uuid1().hex
		doc['_id'] = doc['doc_ID']
	return data
def get_changes():	
	s = couchdb.Server(config['couchdb.url'])
	incoming_database = s[config['couchdb.db.incoming']]
	last_change_sequence = incoming_database.info()['update_seq']
	change_settings = copy.deepcopy(_DEFAULT_CHANGE_OPTIONS)
	change_settings['since'] = last_change_sequence
	#ignore all documents currently in DB
	data = load_data()
	initial_doc_count = incoming_database.info()['doc_count']
	incoming_database.update(data['documents'])
	changes = incoming_database.changes(**change_settings)
	return changes, incoming_database,initial_doc_count
def test_incoming_delete():
	handler = IncomingCopyHandler()
	changes, incoming_database ,initial_doc_count= get_changes()
	prechanges_handler_thread_count = threading.activeCount()
	ids = []
	for change in changes:
		if 'doc' in change and 'doc_ID' in change['doc']:
			ids.append(change['doc']['doc_ID'])
		handler.handle(change,incoming_database)
	while threading.activeCount() > prechanges_handler_thread_count:
		time.sleep(.5)
	assert incoming_database.info()['doc_count'] == initial_doc_count
	s = couchdb.Server(config['couchdb.url'])
	resource_data_database = s[config['couchdb.db.resourcedata']]
	for i in ids:
		del resource_data_database[i]
def test_incoming_copy():
	handler = IncomingCopyHandler()	
	s = couchdb.Server(config['couchdb.url'])
	resource_data_database = s[config['couchdb.db.resourcedata']]
	changes, incoming_database ,initial_doc_count = get_changes()
	prechanges_handler_thread_count = threading.activeCount()
	ids = []
	for change in changes:
		if 'doc' in change and 'doc_ID' in change['doc']:
			ids.append(change['doc']['doc_ID'])
		handler.handle(change,incoming_database)
	while threading.activeCount() > prechanges_handler_thread_count:
		time.sleep(.5)
	for doc_id in ids:
		assert resource_data_database[doc_id] is not None

def test_compaction_handler():
	handler = CompactionHandler(10)
	s = couchdb.Server(config['couchdb.url'])
	resource_data_database = s[config['couchdb.db.resourcedata']]
	changes = resource_data_database.changes(**_DEFAULT_CHANGE_OPTIONS)
	did_compact_run = False
	designDocs = get_design_docs(resource_data_database)
	for change in changes:
		handler.handle(change,resource_data_database)
		for designDoc in designDocs:
			viewInfo = "{0}/{1}/_info".format(resource_data_database.resource.url, designDoc.id)
			viewInfo = json.load(urllib2.urlopen(viewInfo))
			did_compact_run = did_compact_run or viewInfo['view_index']['compact_running']

	assert did_compact_run

@PublishTestDocs(getTestDataForMetadataFormats(20), "lr-view-handler-test")
def test_view_update_handler():
	handler = UpdateViewsHandler(10)
	s = couchdb.Server(config['couchdb.url'])
	resource_data_database = s[config['couchdb.db.resourcedata']]
	designDocs = get_design_docs(resource_data_database)
	changes = resource_data_database.changes(**_DEFAULT_CHANGE_OPTIONS)
	did_views_update = False
	for change in changes:
		handler.handle(change,resource_data_database)
		for designDoc in designDocs:
			viewInfo = "{0}/{1}/_info".format(resource_data_database.resource.url, designDoc.id)
			viewInfo = json.load(urllib2.urlopen(viewInfo))
			did_views_update = did_views_update or viewInfo['view_index']['updater_running']
			log.debug(did_views_update)
		assert did_views_update







