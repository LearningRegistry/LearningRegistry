# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb threshold change handler class.

Created on August 31, 2011

@author: jpoyau
'''
import logging
import json
import urllib2
import multiprocessing
from base_change_threshold_handler import BaseChangeThresholdHandler

log = logging.getLogger(__name__)

class BaseViewsUpdateHandler(BaseChangeThresholdHandler):
    """Class to update the views of the monitored database based on a change count
        or time threshold.  Derived class is expected to implements the _canHandle
        predicate function to filter what changes should be counted. 
    """
    def _updateView(self, viewUrl):
        log.debug('start view update %s' % viewUrl)
        log.debug(urllib2.urlopen(viewUrl).read())
    def _compactView(self,compactUrl):
        log.debug(urllib2.urlopen(compactUrl).read())
    def _handle (self, change, database):
        log.debug("class: {0} Updating views ...".format(self.__class__.__name__))
        try:
            designDocs = database.view('_all_docs',include_docs=True,
                                                        startkey='_design%2F',endkey='_design0')
            for designDoc in designDocs:
                viewInfo = "{0}/{1}/_info".format(database.resource.url, designDoc.id)
                

                viewInfo = json.load(urllib2.urlopen(viewInfo))
                if (not viewInfo['view_index']['compact_running']):
                    compactUrl = "{0}/_compact/{1}".format(database.resource.url, designDoc.id)
                    multiprocessing.Process(target=self._compactView, args=(compactUrl,)).start()                        
                if (not viewInfo['view_index']['updater_running'] and 
                    designDoc.doc.has_key('views') and len(designDoc.doc['views']) > 0):

                    viewName = "{0}/_view/{1}".format(designDoc.id,designDoc.doc['views'].keys()[0])
                    viewUrl = "{0}/{1}?limit=1".format(database.resource.url,viewName)

                    multiprocessing.Process(target=self._updateView, args=(viewUrl,)).start()
    
        except Exception as e:
            log.error(e)
