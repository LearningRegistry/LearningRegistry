from copy import deepcopy
from jsonschema import validate, Draft3Validator, ValidationError
from lr.schema.validate import LRDraft3Validator
from lr.lib import helpers, SpecValidationException
from pylons import config
from uuid import uuid4


import couchdb, logging, pprint, traceback

log = logging.getLogger(__name__)

appConfig = config['app_conf']

#Default couchdb server that use by all the models when none is provided.
_defaultCouchServer =  couchdb.Server(appConfig['couchdb.url.dbadmin']) 

_ID = "_id"
_REV = "_rev"
_DOC_ID = "doc_ID"

def _createDB(name, server=_defaultCouchServer):
    try:
        server.create(name)
    except Exception as ex:
        pass
    return server[name]


class SchemaBackedModelHelper(object):
    validator_class = LRDraft3Validator

    def __init__(self, schemaRef, defaultDBName, server=_defaultCouchServer):
        self.schema = { "$ref": schemaRef }
        self.defaultDB = _createDB(defaultDBName, server)

    def validate_model(self, model):
        
        model_ref = deepcopy(model)
        #strip couchdb specific stuff before validation
        if _ID in model_ref or _REV in model_ref:
            try:
                del model_ref[_ID]
            except:
                pass

            try:
                del model_ref[_REV]
            except:
                pass

        try:
            validate(model_ref, self.schema, cls=self.validator_class)
        except ValidationError as ve:
            msgs = []
            for err in self.validator_class(self.schema).iter_errors(model_ref):
                msgs.append(err.message)

            raise SpecValidationException(",\n".join(msgs))


    def save(self,  model, database=None, log_exceptions=True, skip_validation=False):
            
            # Make sure the spec data conforms to the spec before saving
            # it to the database
            if not skip_validation:
                self.validate_model(model)
                
            db = database
            # If no database is provided use the default one.
            if db == None:
                db = self.defaultDB
            
            result = {'OK':True}   
            
            try:
                _id, _rev = db.save(model)
                log.debug("SAVED: %s", _id)
                if _ID not in model:
                    model[_ID] = _id

                if _REV not in model:
                    model[_REV] = _rev
                
            except Exception as e:
                result['OK'] = False
                result['ERROR'] = "CouchDB save error:  "+str(e)
                if log_exceptions:
                    log.exception("CouchDB save error:\n%s\n" % (pprint.pformat({ "result": result, "model": model}, indent=4),))
                    log.debug("TRACEBACK: %s", "".join(traceback.format_stack()))    
            return result


_db_resource_data = appConfig['couchdb.db.resourcedata']

_schemaRef_Resource_Data = appConfig['schema.resource_data']
_schemaRef_tombstone = appConfig['schema.tombstone']

class ResourceDataHelper(SchemaBackedModelHelper):
    DOC_ID = _DOC_ID
    TIME_STAMPS = ['create_timestamp', 'update_timestamp', 'node_timestamp']
    REPLICATION_FILTER = "filtered-replication/replication_filter"

    def __init__(self, schemaRef, defaultDBName, server=_defaultCouchServer):
        super(ResourceDataHelper, self).__init__(schemaRef, defaultDBName, server)

    def set_timestamps(self, model, timestamp=None):
        if timestamp == None:
            timestamp = helpers.nowToISO8601Zformat()
            
        for stamp in ResourceDataHelper.TIME_STAMPS:
            if stamp not in model or stamp is 'node_timestamp':
                model[stamp] = timestamp
        return model

    def assign_id(self, model):
        if _DOC_ID not in model:
            model[_DOC_ID] = uuid4().hex

        if _ID not in model:
            model[_ID] = model[_DOC_ID]

    def save(self, model, database=None, log_exceptions=True, skip_validation=False):
        self.assign_id(model)        

        return SchemaBackedModelHelper.save(self, model, database, log_exceptions, skip_validation)

ResourceDataModelValidator = ResourceDataHelper(_schemaRef_Resource_Data, _db_resource_data, _defaultCouchServer)


TombstoneValidator = SchemaBackedModelHelper(_schemaRef_tombstone, _db_resource_data, _defaultCouchServer)


