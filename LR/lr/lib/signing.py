import gnupg, json, re
from pylons import session, config
from lr.lib import oauth
from LRSignature.sign import Sign

_appConfig = config["app_conf"]

def _cmp_version(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

def lrsignature_mapper(row_result, row):
    if "lrsignature" in row["doc"]:
        row_result["lrsignature"] = row["doc"]["lrsignature"]
    else:
        row_result["lrsignature"] = { }


_gpgOpts = {
    "gpgbinary": _appConfig["lr.publish.signing.gpgbin"],
    "gnupghome": _appConfig["lr.publish.signing.gnupghome"],
}

privateKeyID = _appConfig["lr.publish.signing.privatekeyid"]
signer = _appConfig["lr.publish.signing.signer"]
_signOpts = {
    "privateKeyID": privateKeyID,
    "passphrase": _appConfig["lr.publish.signing.passphrase"],
    "gnupgHome": _gpgOpts["gnupghome"],
    "gpgbin": _gpgOpts["gpgbinary"],
    "publicKeyLocations": json.loads(_appConfig["lr.publish.signing.publickeylocations"]),
    "sign_everything": False
}

gpg = gnupg.GPG(**_gpgOpts)

_signer = Sign.Sign_0_21(**_signOpts)


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
            
        if _cmp_version(doc["doc_version"], "0.21.0") >= 0:
            if "identity" not in doc:
                doc["identity"] = {}

            doc["identity"]["submitter"] = submitter
            doc["identity"]["submitter_type"] = "user"
            doc["identity"]["signer"] = signer
        else:
            doc["submitter"] = submitter
            doc["submitter_type"] = "user"


        if _cmp_version(doc["doc_version"], "0.20.0") >= 0:
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





