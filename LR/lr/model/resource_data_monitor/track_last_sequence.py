# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''

Created on August 31, 2011

@author: jpoyau
'''
from datetime import timedelta
from lr.lib.couch_change_monitor import BaseChangeThresholdHandler
from pylons import config
import pprint
import logging

log = logging.getLogger(__name__)

# Create an handler to simply track the process change sequence in database.
# We cannot use the one for the change monitor because it is running on different
# processess.

class TrackLastSequence(BaseChangeThresholdHandler):
    _LAST_CHANGE_SEQ = "sequence_number"
    def __init__(self, sequenceChangeDocId, 
                    countThreshold=25, timeThreshold=timedelta(seconds=60)):
        BaseChangeThresholdHandler.__init__(self, countThreshold, timeThreshold)
        self._sequenceChangeDocId =sequenceChangeDocId
        self._lastSavedSequence = None

    def _initLastSavedSequence(self, database):
        if hasattr(self, '_lastSavedSequence'):
            return 
        if database.get(self._sequenceChangeDocId) is not None:
            self._lastSavedSequence =  database.get(self._sequenceChangeDocId).get(self._LAST_CHANGE_SEQ)
        if self._lastSavedSequence is None:
            self._lastSavedSequence = -1
    
    def _getLastSavedSequence(self, database):
        self._initLastSavedSequence(database)
        return self._lastSavedSequence

    def _saveSequence(self, sequence, database):
        
        # add two the sequence number to take into account for the fact 
        # that remove the document before adding the  new one database. 
        sequence = sequence + 2
        self._lastSavedSequence = sequence
        log.debug("Saving change sequence: {0} ....".format(sequence))
        doc ={"_id":self._sequenceChangeDocId,
                    self._LAST_CHANGE_SEQ : sequence}
        
        try: 
            if self._sequenceChangeDocId in database:
                del database[self._sequenceChangeDocId] 
            database[self._sequenceChangeDocId] = doc
        except Exception as e:
            log.error("\n\nError while saving {0} for dabase{1} \n".format(
                    self._sequenceChangeDocId,  str(database)))
            log.exception(e)
        
    def _canHandle(self, change, database):
        log.debug("lastSavedSequence: {0}\tlast_seq: {1}\n".format(
                     self._getLastSavedSequence(database), str(change)))
        # Return false if the change is the result of pushing our own document.
        if ("doc" in change and self._sequenceChangeDocId != change['doc']['_id']):
            return True
        #return false if the change sequence has not changed since our last sat
        if self._getLastSavedSequence(database) <change.get('last_seq'):
            return True
        return False

    def _handle(self, change, database):
        # Save the sequence before the last to ensure that all the change before
        # the save sequence number has been already processed.
        try:
            self._saveSequence(change['last_seq'], database)
        except:
            log.error(change)
   
