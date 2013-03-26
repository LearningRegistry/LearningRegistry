
from lr.plugins import ITombstonePolicy

import logging, copy

log = logging.getLogger(__name__)


class DefaultTombstonePolicy(ITombstonePolicy):
    def __init__(self):
        ITombstonePolicy.__init__(self)

    def permit(self, original_rd3=None, original_crypto=None, replacement_rd3=None, replacement_crypto=None):
        success = False
        # original doc doesn't exist - okay to create tombstone
        if original_rd3 == None and replacement_rd3 is not None and replacement_crypto.valid == True:
            success = True
        # validate that both fingerprints are the same and both signatures were valid.
        elif (original_crypto != None and original_crypto.pubkey_fingerprint == replacement_crypto.pubkey_fingerprint and
            original_crypto.valid == True and replacement_crypto.valid == True):
            success = True

        log.debug("checking permit? %s replacment: %s ", success, replacement_rd3["doc_ID"])
        # deny otherwise
        return success

    def permit_burial(self, replacement_rd3=None, replacement_crypto=None, graveyard=[], existing_gravestones=[]):
        # import pdb; pdb.set_trace()
        permit = False

        replacement_ids = copy.deepcopy(replacement_rd3["replaces"])
        for tombstone in existing_gravestones:
            try:
                replacement_ids.remove(tombstone["doc_ID"])
            except Exception, e:
                log.debug("Shouldn't have gotten here: %s", e)
                pass

        # default policy says that all replacements must be tombstoned, unless already tombstoned
        if len(replacement_ids) == len(graveyard):
            permit = True

        log.debug("permit_burial: %s", permit)
        return permit

