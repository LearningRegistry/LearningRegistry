
from lr.plugins import ITombstonePolicy



class DefaultTombstonePolicy(ITombstonePolicy):
    def __init__(self):
        ITombstonePolicy.__init__(self)

    def permit(self, original_rd3=None, original_crypto=None, replacement_rd3=None, replacement_crypto=None):
        # original doc doesn't exist - okay to create tombstone
        if original_rd3 == None and replacement_rd3 is not None and replacement_crypto.valid == True:
            return True
        # validate that both fingerprints are the same and both signatures were valid.
        elif (original_crypto != None and original_crypto.pubkey_fingerprint == replacement_crypto.pubkey_fingerprint and
            original_crypto.valid == True and replacement_crypto.valid == True):
            return True

        # deny otherwise
        return False

    def permit_burial(self, replacement_rd3=None, replacement_crypto=None, graveyard=[]):
        # import pdb; pdb.set_trace()
        permit = False
        # default policy says that all replacements must be tombstoned
        if len(replacement_rd3["replaces"]) == len(graveyard):
            permit = True

        return permit

