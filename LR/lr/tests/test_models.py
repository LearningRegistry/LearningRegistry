from pylons import config
from functools import wraps
from datetime import datetime
import urllib2
import couchdb
import json
from lr.model.resource_data_monitor import MonitorResourceDataChanges, IncomingCopyHandler, CompactionHandler, UpdateViewsHandler
import copy
import logging
import uuid
import threading
import time
import unittest

_DEFAULT_CHANGE_OPTIONS = {'feed': 'continuous',
                           'include_docs': True}
log = logging.getLogger(__name__)

s = couchdb.Server(config['couchdb.url.dbadmin'])

change_monitors = MonitorResourceDataChanges.getInstance()

def halt_incoming_monitor(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with change_monitors.incomingChangeMonitor as cm:
            log.error("Halted incoming db monitor")
            kwargs["incoming_monitor"] = cm
            return f(*args, **kwargs)
    return wrapper

def halt_resource_monitor(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with change_monitors.resourceDataChangeMonitor as cm:
            log.error("Halted resource db monitor")
            kwargs["resource_data_monitor"] = cm
            return f(*args, **kwargs)
    return wrapper



def get_design_docs(db):
    return db.view('_all_docs', include_docs=True, startkey='_design%2F', endkey='_design0')


def load_data():
    node = s[config['couchdb.db.node']]
    node_description = node['node_description']
    with open('lr/tests/data/nsdl_dc/data-000000000.json', 'r') as f:
        data = json.load(f)
    for doc in data['documents']:
        the_time = datetime.utcnow()
        doc['publishing_node'] = node_description['node_id']
        doc['create_timestamp'] = the_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        doc['node_timestamp'] = doc['create_timestamp']
        doc['update_timestamp'] = doc['create_timestamp']
        doc['doc_ID'] = uuid.uuid1().hex + ':' + the_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        doc['_id'] = doc['doc_ID']
    return data


def get_changes():
    incoming_database = s[config['couchdb.db.incoming']]
    last_change_sequence = incoming_database.info()['update_seq']
    change_settings = copy.deepcopy(_DEFAULT_CHANGE_OPTIONS)
    change_settings['since'] = last_change_sequence
    #ignore all documents currently in DB
    data = load_data()
    initial_doc_count = incoming_database.info()['doc_count']
    while initial_doc_count > 0:
        time.sleep(.1)
        initial_doc_count = incoming_database.info()['doc_count']
        log.error("Waiting for incoming to empty. Current count %s", initial_doc_count)

    for doc in data['documents']:
        try:
            incoming_database[doc["_id"]] = doc
        except couchdb.ResourceConflict as rc:
            assert rc != None, "Failed inserting into incoming db: %s" % (doc["_id"],)

    added_doc_count = incoming_database.info()['doc_count']

    # incoming_database.update(data['documents'])
    changes = incoming_database.changes(**change_settings)
    return changes, incoming_database, initial_doc_count, added_doc_count-initial_doc_count


def delete_data(db, docs):
    for d in docs['documents']:
        del db[d['_id']]

@halt_incoming_monitor
@halt_resource_monitor
def test_incoming_delete(**kwargs):
    handler = IncomingCopyHandler().getInstance()
    assert handler != None, "Should have a singleton"

    changes, incoming_database, initial_doc_count, num_docs = get_changes()
    prechanges_handler_thread_count = threading.activeCount()
    ids = []

    num_changes = 0

    for change in changes:
        num_changes +=1
        if 'doc' in change and 'doc_ID' in change['doc']:
            ids.append(change['doc']['doc_ID'])
        handler.handle(change, incoming_database)
    
    assert num_changes >= (initial_doc_count + num_docs), "Not enough changes handled. Expected: %(expected)s Got: %(got)s" % {"expected":(initial_doc_count + num_docs), "got":num_changes}


    # while threading.activeCount() > prechanges_handler_thread_count:
    while handler.isRunning():
        time.sleep(.5)
        log.info("Waiting for handler to stop. Current count %s", handler.threadCount())
    assert incoming_database.info()['doc_count'] <= initial_doc_count, "Unexpected counts! Incoming: {0}  Initial Count {1}".format(incoming_database.info()['doc_count'], initial_doc_count)
    resource_data_database = s[config['couchdb.db.resourcedata']]
    for i in ids:
        try:
            del resource_data_database[i]
        except couchdb.ResourceNotFound as rnf:
            log.warning("Unable to delete _id: %s", i, exc_info=1)

@halt_incoming_monitor
@halt_resource_monitor
def test_incoming_copy(**kwargs):
    handler = IncomingCopyHandler().getInstance()
    assert handler != None, "Should have a singleton"

    resource_data_database = s[config['couchdb.db.resourcedata']]
    changes, incoming_database, initial_doc_count, num_docs = get_changes()
    prechanges_handler_thread_count = threading.activeCount()

    num_changes = 0

    ids = []
    for change in changes:
        num_changes +=1
        if 'doc' in change and 'doc_ID' in change['doc']:
            ids.append(change['doc']['doc_ID'])
        handler.handle(change, incoming_database)

    assert num_changes >= (initial_doc_count + num_docs), "Not enough changes handled. Expected: %(expected)s Got: %(got)s" % {"expected":(initial_doc_count + num_docs), "got":num_changes}
    # assert num_changes > 0, "There should be some changes."
    assert len(ids) > 0, "No ID's in changes."
    # while threading.activeCount() > prechanges_handler_thread_count:
    while handler.isRunning():
        time.sleep(.5)
        log.info("Waiting for handler to stop. Current count %s", handler.threadCount())
    for doc_id in ids:
        try:
            assert resource_data_database[doc_id] is not None, "Expected document for _id: %s" % (doc_id)
        except couchdb.ResourceNotFound as rnf:
            assert rnf==None, "Expected to find document for _id: %s" % (doc_id,)

@halt_incoming_monitor
@halt_resource_monitor
def test_compaction_handler(**kwargs):
    resource_data_database = s[config['couchdb.db.resourcedata']]
    data = load_data()
    resource_data_database.update(data['documents'])
    changes = resource_data_database.changes(**_DEFAULT_CHANGE_OPTIONS)
    did_compact_run = False
    designDocs = get_design_docs(resource_data_database)
    handler = CompactionHandler(10)
    count = 0
    for change in changes:
        count += 1
        handler.handle(change, resource_data_database)
        if count % 10 == 1:
            for designDoc in designDocs:
                viewInfo = "{0}/{1}/_info".format(resource_data_database.resource.url, designDoc.id)
                viewInfo = json.load(urllib2.urlopen(viewInfo))
                did_compact_run = did_compact_run or viewInfo['view_index']['compact_running']
                if did_compact_run:
                    break
    assert did_compact_run
    delete_data(resource_data_database, data)

@halt_incoming_monitor
@halt_resource_monitor
def test_view_update_handler(**kwargs):
    handler = UpdateViewsHandler(10)
    resource_data_database = s[config['couchdb.db.resourcedata']]
    designDocs = get_design_docs(resource_data_database)
    changes = resource_data_database.changes(**_DEFAULT_CHANGE_OPTIONS)
    did_views_update = False
    data = load_data()
    resource_data_database.update(data['documents'])
    count = 0
    for change in changes:
        count += 1
        handler.handle(change, resource_data_database)
        if count % 10 == 1:
            for designDoc in designDocs:
                viewInfo = "{0}/{1}/_info".format(resource_data_database.resource.url, designDoc.id)
                viewInfo = json.load(urllib2.urlopen(viewInfo))
                did_views_update = did_views_update or viewInfo['view_index']['updater_running']
                if did_views_update:
                    break
    assert did_views_update
    delete_data(resource_data_database, data)
