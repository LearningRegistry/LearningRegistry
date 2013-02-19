
from lr.plugins import ITombstonePolicy, DoNotPublishError
from lr.lib import signing
import logging

log = logging.getLogger(__name__)

class DefaultSignByProxyTombstonePolicy(ITombstonePolicy):
    def __init__(self):
        ITombstonePolicy.__init__(self)
        self.node_key = None

    def _get_submitter(self, doc):
        submitter = None
        try:
            if signing.cmp_version(doc["doc_version"], "0.21.0") >= 0:
                submitter = doc["identity"]["submitter"]
            else:
                submitter = doc["submitter"]
        except:
            pass
        return submitter
            

    def activate(self):
        ITombstonePolicy.activate(self)
        signing.reloadGPGConfig()
        



    def permit(self, original_rd3=None, original_crypto=None, replacement_rd3=None, replacement_crypto=None):
        self.node_key = signing.get_node_key_info()
        log.debug("checking replacment: %s", replacement_rd3["doc_ID"])
        #import pdb; pdb.set_trace()
        #if this is a sign by proxy, replacement fingerprint would be the same node fingerprint.
        # validate that both fingerprints are the same and both signatures were valid.
        # validate that the submitter is the same
        if (replacement_crypto.valid == True and 
            replacement_crypto.pubkey_fingerprint == self.node_key['fingerprint'] and
            original_crypto.pubkey_fingerprint == replacement_crypto.pubkey_fingerprint and
            original_crypto.valid == True and replacement_crypto.valid == True):

            original_submitter = self._get_submitter(original_rd3)
            replacement_submitter = self._get_submitter(replacement_rd3)

            if (original_submitter != None and replacement_submitter != None and
                original_submitter == replacement_submitter):
                log.debug("allow tombstone")
                return True
            else:
                # deny otherwise and ban publishing
                log.debug("deny tombstone: submitter doesn't match.")
                raise DoNotPublishError()
                return False

        log.debug("default allow")
        
        return True

    def permit_burial(self, replacement_rd3=None, replacement_crypto=None, graveyard=[], existing_gravestones=[]):
        '''Always returns false. Rely upon default_tombstone plugin to do permitting'''
        # import pdb; pdb.set_trace()
        permit = False
        # default policy says that all replacements must be tombstoned
        # if len(replacement_rd3["replaces"]) == len(graveyard):
        #     permit = True

        log.debug("permit_burial: %s", permit)
        return permit

