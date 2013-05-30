# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Created on August 18, 2011

@author: jpoyau
'''
from multiprocessing import Queue
from threading import Thread
import couchdb
import logging, thread
import pprint
from base_change_handler import BaseChangeHandler
from base_change_monitor import BaseChangeMonitor

_DEFAULT_CHANGE_OPTIONS = {'feed': 'continuous',
                           'include_docs':True}

log = logging.getLogger(__name__)
        
class MonitorChanges(BaseChangeMonitor):
    """Class that monitors continously a couchdb database changes to apply a list
    of handlers the changes of the database"""
    # Number time the run will try to restart listening to the feed after an error without
    # any change in change.  This avoid getting stuck in endless loop
    _MAX_ERROR_RESTART = 10
     
    def __init__(self, serverUrl, databaseName,  changeHandlers=None,  changeOptions=None, *args, **kwargs):
        """Waring *args and **kwargs will be run on the different process so the must
            be pickeable and not tied in any way to the calling process otherwise to application
            may get unstable.
        """
        BaseChangeMonitor.__init__(self, None, None, "learningRegistryChangeMonitor", args, kwargs)
        self._serverUrl = serverUrl
        self._databaseName = databaseName
        self._callerThread = None
        self._addHandlerQueue = Queue()
        self._removeHandlerQueue = Queue()
        self._initOptions(changeOptions)
        self._initLastChangeSequence()
        self._initChangeHandlers(changeHandlers)
        self._lock = thread.allocate_lock()
    
    def __enter__(self):
        log.debug("Getting Lock...")
        self._lock.acquire()
        log.debug("Got Lock....")
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
        log.debug("Released Lock....")
        return False


    def _initOptions(self, changeOptions):
        if hasattr(self, "_changeOptions"):
            return
        self._changeOptions = {}
        if isinstance(changeOptions, dict):
            self._changeOptions.update(changeOptions)
        self._changeOptions.update(_DEFAULT_CHANGE_OPTIONS)
        log.debug(pprint.pformat(self._changeOptions))
        
    def _initChangeHandlers(self, handlers):
        """Initialize the change handler set.  Use a set to avoid duplicate change handler"""
        if hasattr(self, "_changeHandlerSet") :
            return
        if isinstance(handlers, BaseChangeHandler):
            self._changeHandlerSet = set([handlers])
        elif hasattr(handlers, '__iter__'):
            self._changeHandlerSet = set(
                [h for h in handlers if isinstance(h, BaseChangeHandler)])
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
            log.debug("Waiting for caller thread to die...\n\n")
            #Poll the caller thread and check if it is still alive.
            while(self._callerThread.is_alive()):
                sleep(1)
            log.debug("Caller thread is longer alive ... terminate self...\n\n")
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
                log.debug(self._database.resource.credentials)
                handler.handle(change, self._database)
            except Exception as e:
                log.error("Cannot run handler " + str(handler.handle))
                log.exception(e)
        #check to see if there is any update in the change handler set
        self._updateChangeHandlerSet()

    def _processChanges(self):
        try:
            #Add the last change sequence options as since 
            self._changeOptions['since'] =  self._lastChangeSequence
            self._lock.acquire()
            changes =  self._database.changes(**self._changeOptions)
            for change in changes:
                self._handleChange(change)
                if 'seq' in change:
                    self._lastChangeSequence = change['seq']
                    log.debug("--Last change sequence: {0}\n\n".format(self._lastChangeSequence))
        finally:
            self._lock.release()

    def addHandler(self, handler):
        #Use queue to deal with cross process
        if isinstance(handler, DatabaseChangeHandler):
            self._addHandlerQueue.put(handler)

    def removeHandler(self, handler):
        #Use queue to deal with cross process
        if isinstance(handler, DatabaseChangeHandler):
            self._removeHandlerQueue.put(handler)

    def lock(self):
        return self._lock

    def run(self):
        #initialize the database in run side
        try:
            self._database = couchdb.Server(self._serverUrl)[self._databaseName]
        except:
            server = couchdb.Server(self._serverUrl)
            self._database = server.create(self._databaseName)    
        # As long as we are running keep monitoring the change feed for changes.
        log.debug("\n\nStart monitoring database : {0} changes PID: {1} since:{2}\n\n".format(
                    str(self._database), self.monitorId, self._lastChangeSequence))
        self._errorCount = 0
        while(self.is_alive() and self._errorCount < self._MAX_ERROR_RESTART):
            try:
                self._processChanges()
                self._errorCount = 0
            except Exception as e:
                log.error("Error processing {0} changes. Restart change monitor....\n\n".format(
                str(self._database.name)))
                log.exception(e)
                self._errorCount = self._errorCount + 1

        if self._errorCount >= self._MAX_ERROR_RESTART:
            log.error("Change monitor for database {0} exceeded max errors\n\n".format(str(self._database)))
    
    def terminate(self):
        BaseChangeMonitor.terminate(self)
        log.debug("\n\n------------I got terminated ...---------------\n\n")
    
    def start(self, callerThread=None):
        if isinstance(callerThread, Thread):
            self._callerThread = callerThread
        self._selfTerminatorThread()
        BaseChangeMonitor.start(self)
  

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)

    class TestHandler(BaseChangeHandler):
        def _canHandle(self, change, database):
            return True
        def _handle(self, change, database):
            print("\n\n-->class:{0}  changes: {1}\n\n".format(self.__class__.__name__, str(change)))

    from base_change_threshold_handler import BaseChangeThresholdHandler
    from datetime import timedelta

    class TestThresholdHandler(BaseChangeThresholdHandler):
        def _canHandle(self, change, database):
            return True;
        def _handle(self, change, database):
            print(" -------Taking action ---------\n\n{0}")

    from base_views_update_handler import BaseViewsUpdateHandler
    class TestViewUpdate(BaseViewsUpdateHandler):
        def _canHandle(self, change, database):
            return True

    h1 = TestHandler()
    h2 = TestThresholdHandler(10, timedelta(seconds=60))
    h3 = TestViewUpdate(5, timedelta(seconds=15))
    
    mon = MonitorChanges('http://127.0.0.1:5984', "resource_data", [h1, h2, h3])
    print ("starting the monitoring .....")
    mon.start()
