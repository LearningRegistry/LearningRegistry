import logging
import pprint
import urllib2
import couchdb
import json
import urlparse
import ConfigParser
import os
from pylons import config
from lr.lib import ModelParser, SpecValidationException,helpers as h
from lr.lib.couch_change_monitor import BaseChangeHandler
from lr.model import ResourceDataModel
from couchdb import ResourceConflict
log = logging.getLogger(__name__)

# this doesn't need to be done... should be handled by pylons.config
# scriptPath = os.path.dirname(os.path.abspath(__file__))
# _PYLONS_CONFIG =  os.path.join(scriptPath, '..', '..', '..', 'development.ini')
# _config = ConfigParser.ConfigParser()
# _config.read(_PYLONS_CONFIG)

_RESOURCE_DISTRIBUTABLE_TYPE = "resource_data_distributable"
_RESOURCE_TYPE = "resource_data"
_DOC_TYPE = "doc_type"
_DOC = "doc"


class IncomingCopyHandler(BaseChangeHandler):
	def __init__(self):
		self._serverUrl = config["couchdb.url"]
		self._targetName = config["couchdb.db.resourcedata"]
		
		s = couchdb.Server(self._serverUrl)
		self._db = s[self._targetName]

	def _canHandle(self, change, database):
		if ((_DOC in change) and (change[_DOC].get(_DOC_TYPE) ==_RESOURCE_DISTRIBUTABLE_TYPE or change[_DOC].get(_DOC_TYPE) == _RESOURCE_TYPE)):
			return True
		return False


	def _handle(self, change, database):

		try:
			newDoc = change[_DOC]
			newDoc['node_timestamp'] = h.nowToISO8601Zformat()
			if newDoc[_DOC_TYPEnewDoc_RESOURCE_DISTRIBUTABLE_TYPE:
				newDoc['_id'] = doc['doc_ID']
				newDoc[_DOC_TYPE] = _RESOURCE_TYPE
			rd = ResourceDataModel(newDoc)
			rd.save()
			del database[newDoc['_id']]
		except SpecValidationException:
			log.error(str(newDoc) + " Fails Validation" )
		except ResourceConflict:
			pass #ignore conflicts
		except Exception as ex:
			log.error(ex)
