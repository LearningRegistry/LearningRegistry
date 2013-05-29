# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Created on August 18, 2011

@author: jpoyau
'''

from multiprocessing import Process
from threading import Thread
import platform

class __BaseDefaultMonitor(Process):
    monitorId = property(lambda self: self.pid, None, None, None)
    def __init__(self, *args, **kwargs):
        Process.__init__(self, *args, **kwargs)

    
class __BaseWindowsMonitor(Thread):
    """Thread based class for the monitoring couchdb database change feed.
       Process does not seem to work on windows """
    def terminate(self):
        pass
            
    def start(self):
        Thread.deamon =True
        Thread.start(self)

    monitorId = property(lambda self :self.name, None, None, None)
 
   
BaseChangeMonitor = __BaseDefaultMonitor

if platform.system() == 'Windows':
    BaseChangeMonitor = __BaseWindowsMonitor
 