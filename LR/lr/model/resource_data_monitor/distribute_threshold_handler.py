# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''
Base couchdb threshold change handler class.

Created on August 31, 2011

@author: jpoyau
'''
import urllib2
import pprint
from lr.lib.couch_change_monitor import BaseChangeThresholdHandler
from pylons import config
import logging
import json
appConfig = config['app_conf']

log = logging.getLogger(__name__)
_RESOURCE_DATA_TYPE = "resource_data"
_DOC_TYPE = "doc_type"
_DOC = "doc"

class DistributeThresholdHandler(BaseChangeThresholdHandler):
    def _canHandle(self, change, database):
        if ((_DOC in change) and 
            (change[_DOC].get(_DOC_TYPE) ==_RESOURCE_DATA_TYPE)) :
                return True
        return False
        
    def _handle(self, change, database):
        log.debug('start distribute')
        data = json.dumps({"dist":"dist"})
        request = urllib2.Request(appConfig['lr.distribute.url'],data,{'Content-Type':'application/json; charset=utf-8'})
        log.debug(pprint.pformat(request))
        try:
            response = urllib2.urlopen(request)   
        except urllib2.HTTPError as err:
            log.warning("Got {0} ERROR when requesting \"{1}\"".format(err.code, request.get_full_url()))

        log.debug('end distribute') 
    
