import logging
import couchdb
from threading import Thread
from pylons import config
from lr.lib import SpecValidationException, helpers as h
from lr.lib.couch_change_monitor import BaseChangeHandler
from lr.model import ResourceDataModel
from couchdb import ResourceConflict
from lr.lib.replacement_helper import ResourceDataReplacement
from lr.lib.schema_helper import ResourceDataModelValidator

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
_ID = "id"
_DOCUMENT_UPDATE_THRESHOLD = 100


class IncomingCopyHandler(BaseChangeHandler):
    def __init__(self):
        self._serverUrl = config["couchdb.url.dbadmin"]
        self._targetName = config["couchdb.db.resourcedata"]
        self.documents = []
        s = couchdb.Server(self._serverUrl)
        self._db = s[self._targetName]
        self.repl_helper = ResourceDataReplacement()

    def _canHandle(self, change, database):
        if ((_DOC in change) and \
            (change[_DOC].get(_DOC_TYPE) == _RESOURCE_DISTRIBUTABLE_TYPE or \
            change[_DOC].get(_DOC_TYPE) == _RESOURCE_TYPE)):
            return True
        return False

    def _handle(self, change, database):
        def handleDocument(newDoc):
            should_delete = True
            try:
                # newDoc['node_timestamp'] = h.nowToISO8601Zformat()
                ResourceDataModelValidator.set_timestamps(newDoc)
                self.repl_helper.handle(newDoc)
                # rd = ResourceDataModel(newDoc)
                # rd.save(log_exceptions=False)
            except SpecValidationException as e:
                log.error(newDoc['_id'] + str(e))
            except ResourceConflict:
                log.error('conflict')
            except Exception as ex:
                should_delete = False  # don't delete something unexpected happend
                log.error(ex)
            if should_delete:
                try:
                    del database[newDoc['_id']]
                except Exception as ex:
                    log.error(ex)
        self.documents.append(change[_DOC])
        if len(self.documents) >= _DOCUMENT_UPDATE_THRESHOLD or len(self.documents) >= database.info()['doc_count']:
            for doc in self.documents:
                t = Thread(target=handleDocument, args=(doc,))
                t.start()
            self.documents = []
