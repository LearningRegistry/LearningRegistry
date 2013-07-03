import gnupg, json, logging, re
from pylons import session, config
from lr.lib import oauth
from lr.util import lrgpg
from LRSignature.sign import Sign
from LRSignature.verify import Verify
from LRSignature.errors import MissingPublicKey
from LRSignature import util

log = logging.getLogger(__name__)


def cmp_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

def lrsignature_mapper(row_result, row):
    if "lrsignature" in row["doc"]:
        row_result["lrsignature"] = row["doc"]["lrsignature"]
    else:
        row_result["lrsignature"] = { }



gpg = None
privateKeyID = None
signer = None
_signer = None
_verifier = None

_KEYSERVERS = [ "pool.sks-keyservers.net" ]


def reloadGPGConfig(appConfig=config["app_conf"]):
    global gpg, privateKeyID, signer, _signer, _verifier

    _gpgOpts = {
        "gpgbinary": appConfig["lr.publish.signing.gpgbin"],
        "gnupghome": appConfig["lr.publish.signing.gnupghome"],
    }
    gpg = lrgpg.LRGPG(**_gpgOpts)

    privateKeyID = appConfig["lr.publish.signing.privatekeyid"]
    signer = appConfig["lr.publish.signing.signer"]

    _signOpts = {
        "privateKeyID": privateKeyID,
        "passphrase": appConfig["lr.publish.signing.passphrase"],
        "gnupgHome": _gpgOpts["gnupghome"],
        "gpgbin": _gpgOpts["gpgbinary"],
        "publicKeyLocations": json.loads(appConfig["lr.publish.signing.publickeylocations"]),
        "sign_everything": False
    }
    _vfyOpts = {
        "gnupgHome": _gpgOpts["gnupghome"],
        "gpgbin": _gpgOpts["gpgbinary"]
    }


    _signer = Sign.Sign_0_21(**_signOpts)
    _verifier = Verify.Verify_0_21(**_vfyOpts)

reloadGPGConfig(config["app_conf"])


def get_verification_info(document, attempt=0):
    try:
        info = _verifier.get_and_verify(document)
        return info
    except MissingPublicKey, e:
        # first try the public keyservers
        if attempt >= 0 and attempt < len(_KEYSERVERS):
            try:
                v = gpg.verify(document["digital_signature"]["signature"])
                res = gpg.recv_keys(_KEYSERVERS[attempt], v.key_id)
            except Exception, e:
                log.info("Problem with getting keys from keyserver: %s", e)
                pass

            # try again...
            return get_verification_info(document, attempt+1)
        # ran out of key servers, try locations in envelope.
        elif attempt == len(_KEYSERVERS):
            try:
                for loc in document["digital_signature"]["key_location"]:
                    keys = []
                    try:
                        keys = util.fetchkeys(loc)
                    except Exception, e:
                        log.info("Problem fetching key from location: %s", e)
                    
                    for key in keys:
                        try:
                            util.storekey(key, gpg.gnupghome, gpg.gpgbinary)
                        except Exception, e:
                            log.info("Problem importing or storing key from location: %s", e)
                            
                # try again...
                return get_verification_info(document, attempt+1)
            except:
                pass


    return None

       
_node_key_info = None
def get_node_key_info():
    global _node_key_info
    if _node_key_info == None or _node_key_info['fingerprint'][-16:] != config["app_conf"]["lr.publish.signing.privatekeyid"][-16:]:
        _node_key_info = gpg.list_keys(privateKeyID)[0]
    return _node_key_info

def get_node_public_key():
    return gpg.export_keys(privateKeyID)
def _is_document_signed(document):
    return "digital_signature" in document and "signature" in document['digital_signature']

def sign_doc(doc, cb=None, session_key="oauth-sign"):
    if _is_document_signed(doc):
        if cb is not None:
            return cb(doc)
        else:
            return doc
    if session_key in session and session[session_key]["status"] == oauth.status.Okay:

        if isinstance(doc,unicode):
            doc = json.loads(doc)

        params = session[session_key]["user"]

        submitter = params["name"]
        try:
            submitter = "{0} <{1}>".format(params["lrsignature"]["full_name"], submitter) 
        except:
            pass
            
        if cmp_version(doc["doc_version"], "0.21.0") >= 0:
            if "identity" not in doc:
                doc["identity"] = {}

            doc["identity"]["submitter"] = submitter
            doc["identity"]["submitter_type"] = "user"
            doc["identity"]["signer"] = signer
        else:
            doc["submitter"] = submitter
            doc["submitter_type"] = "user"


        if cmp_version(doc["doc_version"], "0.20.0") >= 0:
            if cb == None:
                return _signer.sign(doc)
            else:
                return cb(_signer.sign(doc))
        else:
            if cb == None:
                return doc
            else:
                return cb(doc)
    elif cb == None:
        return doc
    else:
        return cb(doc)





