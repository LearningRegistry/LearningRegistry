#!/usr/bin/env python
#    Copyright 2011 Lockheed Martin
#
'''
Created on Nov 11, 2011

@author: jpoyau
'''

import signal
import platform
import subprocess
import os
from os import path

class __BaseNodeProcess(object):
    def __init__(self, nodeName, pylonsConfigFilePath, logFilePath, *args, **kwargs):
        self._nodeName = nodeName
        self._pylonsConfigFilePath = pylonsConfigFilePath
        self._logFilePath = logFilePath
    
    def start(self):
       raise NotImpletedError("Please implement me")
    
    def stop(self):
       raise NotImpletedError("Please implement me")
   
       
class __WindowsNodeProcess(__BaseNodeProcess):
    
    def start(self):
        # Save the windows title (use the object id to make it unique)
        # so that it can used in by stop method node using the taskkill
        # command filtering on the  the windows title.
        self._windowTitle = '{0}_{1}'.format(self._nodeName, id(self))
        command = 'START "{0}" /MIN /d {1} paster serve {2} --log-file {3}'.format(
                                          self._windowTitle,
                                          path.abspath(path.dirname(self._pylonsConfigFilePath)),
                                          self._pylonsConfigFilePath, 
                                          self._logFilePath)
        print("\n\nWindows command: {0}\n\n".format(command))
        subprocess.Popen(command, shell=True)
        
    def stop(self):
         command = 'taskkill /F /T /FI "Windowtitle eq {0}"'.format(self._windowTitle)
         print("\n\nTerminate command {0}\n\n".format(command))
         subprocess.Popen(command, shell=True)
         

class __DefaultNodeProcess(__BaseNodeProcess):
    def start(self):
        command = '(cd {0}; paster serve {1} --log-file {2})'.format(
                                        path.abspath(path.dirname(self._pylonsConfigFilePath)),
                                        self._pylonsConfigFilePath, 
                                        self._logFilePath)
        self._pylonsProcess = subprocess.Popen(command, shell=True,preexec_fn=os.setsid)
        
    def stop(self):
        os.killpg(self._pylonsProcess.pid, signal.SIGTERM)   

                
NodeProcess = __DefaultNodeProcess

if platform.system() == 'Windows':
    NodeProcess = __WindowsNodeProcess