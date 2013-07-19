# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
View Compaction class.

Created on August 31, 2011

@author: jklo
'''
import logging
import json
import base64
import urllib2
import multiprocessing
from lr.lib.couch_change_monitor.base_change_threshold_handler import BaseChangeThresholdHandler
log = logging.getLogger(__name__)


class CompactionHandler(BaseChangeThresholdHandler):
    """Class to compact the views of the monitored database based on a change count
        or time threshold.  Derived class is expected to implements the _canHandle
        predicate function to filter what changes should be counted.
    """

    def _canHandle(self, change, database):
        """Since we don't care what what kind of doc this is, just return true."""
        return True

    def _compactView(self, compactUrl, credentials):
        log.debug('start view compaction %s' % compactUrl)
        #curl -H "Content-Type: application/json" -X POST http://localhost:5984/dbname/_compact/designname

        req = urllib2.Request(compactUrl, data="", headers={"Content-Type": "application/json"})
        if credentials is not None and len(credentials) > 0:
            base64string = base64.encodestring('%s:%s' % credentials).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)
        log.debug(urllib2.urlopen(req).read())

    def _handle(self, change, database):
        log.debug("class: {0} Updating views ...".format(self.__class__.__name__))
        try:
            designDocs = database.view('_all_docs', include_docs=True,
                                       startkey='_design%2F', endkey='_design0')
            for designDoc in designDocs:
                viewInfo = "{0}/{1}/_info".format(database.resource.url, designDoc.id)
                viewInfo = json.load(urllib2.urlopen(viewInfo))
                if (not viewInfo['view_index']['updater_running'] and
                    not viewInfo['view_index']['compact_running'] and
                    'views' in designDoc.doc and len(designDoc.doc['views']) > 0):
                    designName = designDoc.id.split('/')[1]
                    # http://localhost:5984/dbname/_compact/designname
                    compactName = "_compact/{0}".format(designName)
                    compactUrl = '/'.join([database.resource.url, compactName])
                    auth = database.resource.credentials
                    multiprocessing.Process(target=self._compactView, args=(compactUrl, auth)).start()
        except Exception as e:
                    log.error(e)
