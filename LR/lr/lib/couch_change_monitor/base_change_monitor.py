# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Created on August 18, 2011

@author: jpoyau
'''

from multiprocessing import Process
from threading import Thread
import platform

class __BaseProcessMonitor(Process):
    monitorId = property(lambda self: self.pid, None, None, None)
    def __init__(self, *args, **kwargs):
        Process.__init__(self, *args, **kwargs)


class __BaseThreadMonitor(Thread):
    """Thread based class for the monitoring couchdb database change feed.
       Process does not seem to work on windows """
    def terminate(self):
        pass

    def start(self):
        Thread.daemon =True
        Thread.start(self)

    monitorId = property(lambda self :self.name, None, None, None)


# Using thread monitor over process-based monitor as process monitor creates zombies and
# errors due to main process + workers confusing who owns child processes
BaseChangeMonitor = __BaseThreadMonitor


