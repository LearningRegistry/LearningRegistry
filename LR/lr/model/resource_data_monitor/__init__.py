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
from pylons import config

appConfig = config['app_conf']
log = logging.getLogger(__name__)

_RESOURCE_DATA_CHANGE_ID =  "_local/Last_Processed_Change_Sequence"

_RESOURCE_DATA_CHANGE_HANDLERS=[
    TrackLastSequence(_RESOURCE_DATA_CHANGE_ID),
    DistributableHandler(),
    ResourceDataHandler(),
    UpdateViewsHandler(appConfig['couchdb.threshold.viewupdate']),
    DistributeThresholdHandler(appConfig['couchdb.threshold.distributes'])
    ]

def _getLastSavedSequence():
    lastSavedSequence = -1
    if _RESOURCE_DATA_CHANGE_ID in ResourceDataModel._defaultDB:
        lastSavedSequence=ResourceDataModel._defaultDB[_RESOURCE_DATA_CHANGE_ID][TrackLastSequence._LAST_CHANGE_SEQ]
    return lastSavedSequence

    
def monitorResourceDataChanges(): 
    options = {'since':_getLastSavedSequence()}
    log.debug("\n\n-----"+pprint.pformat(options)+"------\n\n")

    changeMonitor = MonitorChanges(appConfig['couchdb.url'], 
                                                            appConfig['couchdb.db.resourcedata'],
                                                            _RESOURCE_DATA_CHANGE_HANDLERS,
                                                            options)
    changeMonitor.start()
    
    #changeMonitor.start(threading.current_thread())
    def atExitHandler():
        changeMonitor.terminate()
        log.debug("Last change {0}\n\n".format(changeMonitor._lastChangeSequence))

    atexit.register(atExitHandler)
