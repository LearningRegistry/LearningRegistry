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
from compaction_handler import CompactionHandler
from pylons import config

appConfig = config['app_conf']
log = logging.getLogger(__name__)

_CHANGE_ID =  "_local/Last_Processed_Change_Sequence"

_RESOURCE_DATA_CHANGE_HANDLERS=[
    TrackLastSequence(_CHANGE_ID),
    UpdateViewsHandler.getInstance(appConfig['couchdb.threshold.viewupdate']),
    DistributeThresholdHandler.getInstance(appConfig['couchdb.threshold.distributes']),
    CompactionHandler.getInstance(appConfig['couchdb.threshold.compaction'])
    ]

_INCOMING_CHANGE_HANDLERS=[
    TrackLastSequence(_CHANGE_ID),
    IncomingCopyHandler.getInstance()
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

    
class MonitorResourceDataChanges(object): 
    
    _instance = None

    @classmethod
    def getInstance(cls, *args, **kwargs):
        if cls._instance == None:
            cls._instance = cls()

        return cls._instance


    def __init__(self, *args, **kwargs):
        options = {'since':_getLastSavedSequence()}
        log.debug("\n\n-----"+pprint.pformat(options)+"------\n\n")
        print('got here')
        self.resourceDataChangeMonitor = MonitorChanges(appConfig['couchdb.url.dbadmin'], 
                                                            appConfig['couchdb.db.resourcedata'],
                                                            _RESOURCE_DATA_CHANGE_HANDLERS,
                                                            options)
        self.resourceDataChangeMonitor.start()
            
        self.incomingChangeMonitor = MonitorChanges(appConfig['couchdb.url.dbadmin'], 
                                                            incomingDB,
                                                            _INCOMING_CHANGE_HANDLERS,
                                                            {'since':-1})
        self.incomingChangeMonitor.start()
        

        #changeMonitor.start(threading.current_thread())
        def atExitHandler():
            
            self.resourceDataChangeMonitor.terminate()
            self.incomingChangeMonitor.terminate()
            log.debug("Last change in Resource Data: {0}\n\n".format(self.resourceDataChangeMonitor._lastChangeSequence))        
            log.debug("Last change in Incoming: {0}\n\n".format(self.incomingChangeMonitor._lastChangeSequence))

        atexit.register(atExitHandler)
