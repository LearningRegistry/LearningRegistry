import lr.lib.signing as s
from lr.util.decorators import make_gpg_keys
import json
from functools import wraps

def modify_keyserver(keyserver_list=[]):
    def wrapped(fn):
        @wraps(fn)
        def _wrapped(*args, **kw):
            orig_keyservers = s._KEYSERVERS
            s._KEYSERVERS = keyserver_list
            try:
                fn(*args, **kw)
            finally:
                s._KEYSERVERS = orig_keyservers

        return _wrapped
    return wrapped

# Don't use a keyserver
@modify_keyserver([])
@make_gpg_keys(1)
def test_fetchSelfHostedKey(*args, **kw):
    doc = {
        "doc_type": "resource_data",
        "replaces": ["804026fc367a4a44a76bd5b4c24809d8"],
        "update_timestamp": "2013-06-25T10:32:28.373753Z",
        "digital_signature": {
            "key_location": ["http://www.oercommons.org/public-key.txt"],
            "key_owner": "OER Commons <info@oercommons.org>",
            "signing_method": "LR-PGP.1.0",
            "signature": "-----BEGIN PGP SIGNED MESSAGE-----\nHash: SHA1\n\n47766650c7a3a81409e53161c918e9312994718e7d8d2a0c67ed6bb05d83566a\n-----BEGIN PGP SIGNATURE-----\nVersion: GnuPG v1.4.11 (Darwin)\nComment: GPGTools - http://gpgtools.org\n\niQEcBAEBAgAGBQJRyXG7AAoJEKPVkXeiZE8+R8UH/RVyspUdg1+iUiRG5+hIlsFl\ndgccEKubzTmps3G6vIOD7LEmObx23/dMhQiQByOvqLyjQkSv1E9E9NL/aOCGE7X4\nWUDaV5EheHKnnEP2q4w91qPuJ9GKU2XIE0n8wQVSLjFTju9Oc0IsFQMERbiew+WD\nwRwmc2SiaJBmLQ68fmEht07+R/fBw0aoHVl3lt+tz7VKao2A5+L3QHMQqwaILBdV\nJysFtSrrz3s2lopuuG4hRz+2rh/tPQwUWUS+kABg2s073Tt+fahHHekuG5ugamU8\nzzcNysozxFQACk4pbSGc7f/V8hxRFo6V5XxLjfgS06QfMFkdDFn7sbL3nB58oaA=\n=jBP2\n-----END PGP SIGNATURE-----\n"
        },
        "TOS": {
            "submission_TOS": "http://www.learningregistry.org/tos/cc0/v0-5/"
        },
        "_rev": "1-d0879e7751add53f72d1672dec4a70da",
        "resource_data_type": "paradata",
        "payload_placement": "none",
        "node_timestamp": "2013-06-25T10:32:28.373753Z",
        "doc_version": "0.49.0",
        "create_timestamp": "2013-06-25T10:32:28.373753Z",
        "active": True,
        "publishing_node": "bababe6a3288497fb7a46d454154f5db",
        "_id": "5569a004388e4621ba8b414969455f8b",
        "doc_ID": "5569a004388e4621ba8b414969455f8b",
        "identity": {
            "submitter": "OER Commons",
            "submitter_type": "agent"
        }
    }

    info = s.get_verification_info(doc)
    assert info != None, "Should have found a key to fetch."
