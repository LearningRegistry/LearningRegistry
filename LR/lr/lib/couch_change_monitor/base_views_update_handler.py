# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb threshold change handler class.

Created on August 31, 2011

@author: jpoyau
'''
import logging
from base_change_threshold_handler import BaseChangeThresholdHandler

log = logging.getLogger(__name__)

class BaseViewsUpdateHandler(BaseChangeThresholdHandler):
    """Class to update the views of the monitored database based on a change count
        or time threshold.  Derived class is expected to implements the _canHandle
        predicate function to filter what changes should be counted. 
    """
    def _handle (self, change, database):
        log.debug("class: {0} Updating views ...".format(self.__class__.__name__))
        try:
            designDocs = database.view('_all_docs',include_docs=True,
                                                            startkey='_design%2F',endkey='_design0')
            for designDoc in designDocs:
                try:
                    if designDoc.doc.has_key('views') and len(designDoc.doc['views']) > 0:
                        viewName = "{0}/_view/{1}".format(designDoc.id,designDoc.doc['views'].keys()[0])
                        log.debug("class:{0} start view update %s".format(self.__class__.__name__, viewName))
                        log.debug(len(database.view(viewName))) 
                except Exception as e:
                    log.error(e)
        except Exception as e:
            log.error(e)
