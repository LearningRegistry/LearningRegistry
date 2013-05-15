# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb change handler class.

Created on August 18, 2011

@author: jpoyau
'''


class BaseChangeHandler(object):

    singleton_instance = None
    @classmethod
    def getInstance(cls, *args, **kwargs):
        if cls.singleton_instance == None:
            cls.singleton_instance = cls(*args, **kwargs)
        return cls.singleton_instance

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
