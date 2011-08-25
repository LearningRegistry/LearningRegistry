#!/usr/bin/python
from multiprocessing import Process, Queue
import couchdb
import logging
from threading import Thread
from time import sleep
import pprint
from datetime import timedelta, datetime

#!/usr/bin/pyton

#    Copyright 2011 Lockheed Martin

'''
Created on August 18, 2011

@author: jpoyau
'''



_DEFAULT_CHANGE_OPTIONS = {'feed': 'continuous',
                                                    'include_docs':True}

log = logging.getLogger(__name__)

class DatabaseChangeHandler(object):
    def _canHandle(self, change, database):
        """Handler subclass must implement. Returns True if the handler object can or
        wants to handle the change. Otherwise returns False."""
        raise NotImplementedError, "Implement me"
        
    def _handle(self, change, database):
        """Pass the database, since the handler code will be running
        in the same process as the monitor"""
        raise NotImplementedError, "Implement me"
        
    def handle(self, change, database):
        if self._canHandle(change, database):
            self._handle(change, database)

class DatabaseChangeThresholdHandler(DatabaseChangeHandler):
    def __init__(self,  predicate, action, countThreshold, timeThreshold=timedelta.max):
        self._countThreshold = int(countThreshold)
        self._timeThreshold = timeThreshold
        self._resetChangeToThreshold()
        self._predicate = predicate
        self._action = action
    
    def _resetChangeToThreshold(self):
         self._changeCount = 0
         self._lastActionTime = datetime.now() 
         
    def _canHandle(self, change, database):
        return self._predicate(change, database)
    
    def _shouldTakeAction(self):
        log.info("count: {0} countThreshold: {1} timedelta: {2} timethreshold: {3}".format(
                     self._changeCount, self._countThreshold, 
                     (datetime.now() -self._lastActionTime) , self._timeThreshold))
                     
        if ((self._changeCount >= self._countThreshold) or
            ((datetime.now() - self._lastActionTime)  >= self._timeThreshold)):
            return True
        return False
        
    def _handle(self, change, database):
        self._changeCount = self._changeCount + 1
        if self._shouldTakeAction():
            self._action(change, database)
            self._resetChangeToThreshold()


class MonitorDatabaseChanges(Process):
    """Class that monitors continously a couchdb database changes to apply a list
    of handlers the changes of the database"""
    # Number time the run will try to restart listening to the feed after an error without
    # any change in change.  This avoid getting stuck in endless loop
    _MAX_ERROR_RESTART = 10
     
    def __init__(self, serverUrl, databaseName,  changeHandlers=None,  changeOptions=None, *args, **kwargs):
        Process.__init__(self, None, None, "learningRegistryChangeMonitor", args, kwargs)
        self._database = couchdb.Server(serverUrl)[databaseName]
        self._callerThread = None
        self._addHandlerQueue = Queue()
        self._removeHandlerQueue = Queue()
        self._initOptions(changeOptions)
        self._initLastChangeSequence()
        self._initChangeHandlers(changeHandlers)
    
    def _initOptions(self, changeOptions):
        if hasattr(self, "_changeOptions"):
            return
        self._changeOptions = {}
        if isinstance(changeOptions, dict):
            self._changeOptions.update(changeOptions)
        self._changeOptions.update(_DEFAULT_CHANGE_OPTIONS)
        log.info(pprint.pformat(self._changeOptions))
        
    def _initChangeHandlers(self, handlers):
        if hasattr(self, "_changeHandlerSet") :
            return
        if isinstance(handlers, DatabaseChangeHandler):
            self._changeHandlerSet = set([handlers])
        elif hasattr(handlers, '__iter__'):
            self._changeHandlerSet = set(
                [h for h in handlers if isinstance(h, DatabaseChangeHandler)])
        else: 
            self._changeHandlerSet = set()

    def _initLastChangeSequence(self):
        """Get the last sequence change on startup assuming that the  previous changes
            where handle"""
        if hasattr(self, '_lastChangeSequence') == False:
            #Check to see if the options contains a last change sequence key.
            if 'since' in self._changeOptions.keys():
                self._lastChangeSequence = self._changeOptions['since']
            else:
                self._lastChangeSequence =-1
    
    def _selfTerminatorThread(self):
        """Method that starts a thread that will monitor the caller thread that started
        this object.  When  the caller thread is longer alive stop the monitoring """
        if self._callerThread is None:
            return
        #Simple thread run function watches the caller thread.
        def callerWatcher():
            log.info("Waiting for caller thread to die...")
            #Poll the caller thread and check if it is still alive.
            while(self._callerThread.is_alive()):
                sleep(1)
            log.info("Caller thread is longer alive ... terminate self...")
            self.terminate()
        
        terminator = Thread(target=callerWatcher)
        terminator.start()

    
    def _updateChangeHandlerSet(self):
        #Check to add and remove handler queue and update hander set.
        while(self._addHandlerQueue.empty() ==False):
            self._changeHandlerSet.add(self._addHandlerQueue.get())
            
        while(self._removeHandlerQueue.empty() == False):
            self._changeHandlerSet.remove(self._removeHandlerQueue.get())
        
    def  _handleChange(self, change):
        #call all change handlers
        for handler in self._changeHandlerSet:
            try:
                handler.handle(change, self._database)
            except Exception as e:
                log.error("Cannot run handler "+str(handler.handle))
                log.exception(e)
        #check to see if there is any update in the change handler set
        self._updateChangeHandlerSet()

    def _processChanges(self):
        #Add the last change sequence options as since 
        self._changeOptions['since'] =  self._lastChangeSequence
        changes =  self._database.changes(**self._changeOptions)
        for change in changes:
            self._handleChange(change)
            if 'seq' in change:
                self._lastChangeSequence = change['seq']
                log.info("--Last change sequence: {0}".format(self._lastChangeSequence))

    def addHandler(self, handler):
        if isinstance(handler, DatabaseChangeHandler):
            self._addHandlerQueue.put(handler)

    def removeHandler(self, handler):
        if isinstance(handler, DatabaseChangeHandler):
            self._removeHandlerQueue.put(handler)

    def run(self):
        # As long as we are running keep monitoring the change feed for changes.
        log.info("\n\n\nStart monitoring database : {0} changes PID: {1} since:{2}".format(
                    str(self._database), self.pid, self._lastChangeSequence))
        self._errorCount = 0
        while(self.is_alive() and self._errorCount < self._MAX_ERROR_RESTART):
            try:
                self._processChanges()
                self._errorCount = 0
            except Exception as e:
                log.error("\n\n\nError processing {0} changes. Restart change monitor....".format(
                str(self._database.name)))
                log.exception(e)
                self._errorCount = self._errorCount + 1
                
        if self._errorCount >= self._MAX_ERROR_RESTART:
            log.error("Change monitor for database {0} exceeded max errors".format(str(self._database)))
    
    def terminate(self):
        Process.terminate(self)
        log.info("\n\n------------I got terminated ...---------------\n\n")
    
    def start(self, callerThread=None):
        if isinstance(callerThread, Thread):
            self._callerThread = callerThread
        self._selfTerminatorThread()
        Process.start(self)

if __name__=="__main__":
    
    logging.basicConfig()
    
    class TestHandler(DatabaseChangeHandler):
        def _canHandle(self, change, database):
            return True
        def _handle(self, change, database):
            print(str(change))
            
    h = TestHandler()
    server = couchdb.Server('http://127.0.0.1:5984') 
    db = server["resource_data"]
    mon = MonitorDatabaseChanges(db, h)
    print ("starting the monitoring .....")
  
    
