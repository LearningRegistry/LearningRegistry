from lr.plugins import ITombstonePolicy, DoNotPublishError
from pylons import config
from pprint import pprint
from os import walk
from lr.lib.signing import gpg

import logging, copy

log = logging.getLogger(__name__)


class AdminSignedTombstone(ITombstonePolicy):
    def __init__(self):
        super(ITombstonePolicy, self).__init__()

        self.public_key_fingerprints = []

    def activate(self):
        super(ITombstonePolicy, self).activate()

        public_key_directory = config['app_conf']['lr.tombstone.admin_signed.key_directory']

        for (dirpath, dirnames, filenames) in walk(public_key_directory):
            for f in filenames:
                if f[-4:] == '.txt':
                    with open(dirpath+f, 'r') as key_file:
                        self.public_key_fingerprints.extend(gpg.import_keys(key_file.read()).fingerprints)
                        print "Loading key from %s%s" % (dirpath, f)



    def permit(self, original_rd3=None, original_crypto=None, replacement_rd3=None, replacement_crypto=None):

        # if the public key fingerprint used for signing the replacement
        # request is among our admin list, then permit deletion
        result =  replacement_crypto.pubkey_fingerprint in self.public_key_fingerprints

        log.debug("Checking if signer is amongst admin keys: %s" % result)
        return result

    def permit_burial(self, replacement_rd3=None, replacement_crypto=None, graveyard=[], existing_gravestones=[]):
        # abide the default policy
        permit = False

        return permit

