# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb threshold change handler class.

Created on August 18, 2011

@author: jpoyau
'''

import pprint
import logging
from lr.lib import MonitorChanges
import atexit
from lr.model import ResourceDataModel
from distributable_handler import DistributableHandler
from resource_data_handler import ResourceDataHandler
from update_views_handler import  UpdateViewsHandler
from distribute_threshold_handler import DistributeThresholdHandler
from track_last_sequence import TrackLastSequence
from incoming_copy_handler import IncomingCopyHandler
from pylons import config

appConfig = config['app_conf']
log = logging.getLogger(__name__)

_CHANGE_ID =  "_local/Last_Processed_Change_Sequence"

_RESOURCE_DATA_CHANGE_HANDLERS=[
    TrackLastSequence(_CHANGE_ID),
    UpdateViewsHandler(appConfig['couchdb.threshold.viewupdate']),
    DistributeThresholdHandler(appConfig['couchdb.threshold.distributes'])
    ]

_INCOMING_CHANGE_HANDLERS=[
    TrackLastSequence(_CHANGE_ID),
    IncomingCopyHandler()
    ]

try:
    incomingDB = appConfig['couchdb.db.incoming']
except:
    incomingDB = 'incoming'

def _getLastSavedSequence():
    lastSavedSequence = -1
    if _CHANGE_ID in ResourceDataModel._defaultDB:
        lastSavedSequence=ResourceDataModel._defaultDB[_CHANGE_ID][TrackLastSequence._LAST_CHANGE_SEQ]
    return lastSavedSequence

    
def monitorResourceDataChanges(): 
    options = {'since':_getLastSavedSequence()}
    log.debug("\n\n-----"+pprint.pformat(options)+"------\n\n")
    
    resourceDataChangeMonitor = MonitorChanges(appConfig['couchdb.url'], 
                                                        appConfig['couchdb.db.resourcedata'],
                                                        _RESOURCE_DATA_CHANGE_HANDLERS,
                                                        options)
    resourceDataChangeMonitor.start()
        
    incomingChangeMonitor = MonitorChanges(appConfig['couchdb.url'], 
                                                        incomingDB,
                                                        _INCOMING_CHANGE_HANDLERS,
                                                        options)
    incomingChangeMonitor.start()
    

    #changeMonitor.start(threading.current_thread())
    def atExitHandler():
        
        resourceDataChangeMonitor.terminate()
        incomingChangeMonitor.terminate()
        log.debug("Last change in Resource Data: {0}\n\n".format(resourceDataChangeMonitor._lastChangeSequence))        
        log.debug("Last change in Incoming: {0}\n\n".format(incomingChangeMonitor._lastChangeSequence))

    atexit.register(atExitHandler)
