import gnupg, json
from pylons import session, config
from lr.lib import oauth
from LRSignature.sign import Sign

_appConfig = config["app_conf"]

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
    "publicKeyLocations": json.loads(_appConfig["lr.publish.signing.publickeylocations"])
}

gpg = gnupg.GPG(**_gpgOpts)

_signer = Sign.Sign_0_21(**_signOpts)


def get_node_public_key():
    return gpg.export_keys(privateKeyID)

def sign_doc(doc, cb=None):
    if session["oauth-sign"]["status"] == oauth.authorize.Okay:

        if isinstance(doc,unicode):
            doc = json.loads(doc)

        params = session["oauth-sign"]["user"]

        submitter = params["name"]
        try:
            submitter = "{0} <{1}>".format(params["lrsignature"]["full_name"], submitter) 
        except:
            pass
            
        if "identity" not in doc:
            doc["identity"] = {}

        doc["identity"]["submitter"] = submitter
        doc["identity"]["submitter_type"] = "user"
        doc["identity"]["signer"] = signer

        if cb == None:
            return _signer.sign(doc)
        else:
            return cb(_signer.sign(doc))






