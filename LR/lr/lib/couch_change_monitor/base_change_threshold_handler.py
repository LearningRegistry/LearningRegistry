# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb threshold change handler class.

Created on August 18, 2011

@author: jpoyau
'''
from datetime import timedelta, datetime
import logging
from base_change_handler import BaseChangeHandler
log = logging.getLogger(__name__)

class BaseChangeThresholdHandler(BaseChangeHandler):
    def __init__(self, countThreshold, timeThreshold=timedelta.max):
        self._countThreshold = int(countThreshold)
        self._timeThreshold = timeThreshold
        self._changeCount = 0
        self._lastActionTime = datetime.now()

    def _resetChangeToThreshold(self):
        """Resets each threshold independently"""
        if self._changeCount >= self._countThreshold:
            self._changeCount = 0
        if (datetime.now() - self._lastActionTime)  >= self._timeThreshold:
            self._lastActionTime = datetime.now()

    def _shouldTakeAction(self):
        # log.debug("class: {0} count: {1} countThreshold: {2} timedelta: {3} timethreshold: {4}\n\n".format(
        #              self.__class__.__name__, self._changeCount, self._countThreshold,
        #              (datetime.now() -self._lastActionTime) , self._timeThreshold))

        if ((self._changeCount >= self._countThreshold) or
            ((datetime.now() - self._lastActionTime)  >= self._timeThreshold)):
            # log.debug("class: {0} Willl take action ...".format(self.__class__.__name__))
            return True
        return False

    def handle(self, change, database):
        #check to see if we can care about the change. if so increase the count.
        if self._canHandle(change, database):
            self._changeCount = self._changeCount + 1

            if self._shouldTakeAction():
                self._handle(change, database)
                self._resetChangeToThreshold()
