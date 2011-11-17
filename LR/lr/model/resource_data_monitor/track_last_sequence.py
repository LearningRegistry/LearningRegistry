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
     
    def _saveSequence(self, sequence, database):
        log.debug("Last process change sequence: {0}".format(sequence))
        doc ={"_id":self._sequenceChangeDocId,
                    self._LAST_CHANGE_SEQ : sequence}
        try:
            if self._sequenceChangeDocId in database:
                del database[self._sequenceChangeDocId]
            database[self._sequenceChangeDocId] = doc
        except Exception as e:
            log.error("\n\nError while saving {0} for dabase{1} \n".format(
                    self._sequenceChangeDocId, str(database)))
            log.exception(e)

    def _canHandle(self, change, database):
        return (('doc' in change) and ('seq' in change))

    def _handle(self, change, database):
        # Save the sequence before the last to ensure that all the change before
        # the save sequence number has been already processed.
        try:
            self._saveSequence(change['seq'], database)
        except:
            log.error(change)
   
