from pylons import config
from lr.lib import SpecValidationException
from lr.lib.signing import get_verification_info
from lr.lib.helpers import nowToISO8601Zformat
from lr.plugins import LRPluginManager, ITombstonePolicy
from lr.lib.schema_helper import ResourceDataModelValidator

import copy, couchdb, logging


log = logging.getLogger(__name__)

appConfig = config['app_conf']

#Default couchdb server that use by all the models when none is provided.
_defaultCouchServer =  couchdb.Server(appConfig['couchdb.url.dbadmin']) 
_db_resource_data = appConfig['couchdb.db.resourcedata']

_DOC_VERSION = "doc_version"
_REPLACES = "replaces"


_TOMBSTONE_TEMPLATE = {
    "doc_ID": None,
    "doc_type": "tombstone",
    "doc_version": "0.49.0",
    "replaces": [],
    "replaced_by": {
        "doc_ID": None,
        "public_key_fingerprint": None,
        "public_key_locations": []
    },
    "create_timestamp":None,
    "resource_locator": None,
    "do_not_distribute": True
}

def makeTombstone(replacement_doc, replacement_info, orig_doc_id, orig_doc=None):
    tombstone = copy.deepcopy(_TOMBSTONE_TEMPLATE)
    tombstone.update({
        "doc_ID": orig_doc_id,
        "create_timestamp": nowToISO8601Zformat()
    })
    if orig_doc is not None:
        tombstone["resource_locator"] = orig_doc["resource_locator"]

        if "replaces" in orig_doc:
            tombstone["replaces"] = orig_doc["replaces"]
        else:
            del tombstone["replaces"]

    tombstone["replaced_by"].update({
            "doc_ID": replacement_doc["doc_ID"],
            "public_key_fingerprint": replacement_info.pubkey_fingerprint,
            "public_key_locations": replacement_doc["digital_signature"]["key_location"]
        })
    return tombstone


class ResourceDataReplacement():

    def __init__(self, defaultDBName=_db_resource_data, server=_defaultCouchServer):
        self.db = self._createDB(defaultDBName, server)
    
    def _createDB(self, name, server):
        try:
            server.create(name)
        except Exception as ex:
            pass
        return server[name]

    def _make_tombstone(self, replacement_rd3, replacement_rd3_info, orig_doc_id, orig_doc):
        
        tombstone = makeTombstone(replacement_rd3, replacement_rd3_info, orig_doc_id, orig_doc)

        tombstone["_id"] = tombstone["doc_ID"]
        try:
            tombstone["_rev"] = orig_doc["_rev"]
        except:
            pass

        return tombstone


    def _check_if_permitted(self, replacement_rd3, replacement_rd3_info, orig_doc, orig_doc_info):
        # Tombstone logic needs to happen here    
        # import pdb; pdb.set_trace()
        allowTombstone = True
        for plugin in LRPluginManager.getPlugins(ITombstonePolicy.ID):
            try:
                allowTombstone = allowTombstone & plugin.permit(orig_doc, orig_doc_info, replacement_rd3, replacement_rd3_info)
            except Exception, e:
                log.exception("Plugin raised exception: %s", e)
                allowTombstone = False
            
            if not allowTombstone:
                break
        else:
            allowTombstone = True

        return allowTombstone

    def _has_graveyard_permit(self, replacement_rd3, replacement_rd3_info, graveyard):
        grantPermit = True
        for plugin in LRPluginManager.getPlugins(ITombstonePolicy.ID):
            try:
                grantPermit = grantPermit | plugin.permit_burial(replacement_rd3, replacement_rd3_info, graveyard)
            except Exception, e:
                log.exception("Plugin raised exception: %s", e)
                grantPermit = False
                
            if not grantPermit:
                break
        else:
            grantPermit = True

        return grantPermit

    def handle(self, replacement_rd3):
        # assign doc_id if need.
        ResourceDataModelValidator.assign_id(replacement_rd3)

        # validate the rd3 to be published.
        ResourceDataModelValidator.validate_model(replacement_rd3)

        # check to see if it's a replacement
        if replacement_rd3 is not None and _REPLACES in replacement_rd3:
            replacement_rd3_info = get_verification_info(replacement_rd3)
            if replacement_rd3_info is not None:
                graveyard = []
                for orig_doc_id in replacement_rd3[_REPLACES]:
                    try:
                        orig_doc = self.db[orig_doc_id]
                        orig_doc_info = get_verification_info(orig_doc)
                    except couchdb.http.ResourceNotFound as rne:
                        orig_doc = None
                        orig_doc_info = None

                    # verify that tombstones
                    permitted = self._check_if_permitted(replacement_rd3, replacement_rd3_info, orig_doc, orig_doc_info)
                    log.debug("handle: permitted? {0}".format(permitted))
                    if permitted:
                        tombstone = self._make_tombstone(replacement_rd3, replacement_rd3_info, orig_doc_id, orig_doc)               
                        graveyard.append(tombstone)
                    else:
                        log.debug("Replacement resource not permitted to be saved.")


                if self._has_graveyard_permit(replacement_rd3, replacement_rd3_info, graveyard):
                    result = ResourceDataModelValidator.save(replacement_rd3, skip_validation=True)
                    for tombstone in graveyard:
                        self.db[tombstone["_id"]] = tombstone 
                    return result

                else:
                    # import pdb; pdb.set_trace()
                    raise SpecValidationException("Node policy does not permit this resource published.")

        # we get here because it's not a replacement.
        return ResourceDataModelValidator.save(replacement_rd3, skip_validation=True)


                


