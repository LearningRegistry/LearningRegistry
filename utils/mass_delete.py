#!/usr/bin/env python

import copy, re, urllib2, json, ConfigParser, time
import oauth2 as oauth
from urllib import urlencode
from argparse import ArgumentParser
from pprint import pprint
from LRSignature.sign.Sign import Sign_0_21

_consumer = {
	"key": "joe@navnorth.com",
	"secret": "************************************"
}

_token = {
	"key": "node_sign_token",
	"secret": "************************************"
}

_debug_ID = ""

_TOMBSTONE_DOCUMENT = {
    "replaces": [],
    "TOS": {
        "submission_TOS": "http://www.learningregistry.org/tos"
    },
    "active":True,
    "doc_type": "resource_data",
    "doc_version": "0.51.0",
    "identity": {
        "submitter": "",
        "submitter_type": "user"
    },
    "payload_placement": "none",
    "resource_data_type": "metadata"
}

class MassDelete:

    def __init__(self, options):
        self.options = options

        self.server = 'https://'+options['host']+'/'
        self.identity = options['identity']

        if options['key'] is not None and options['key_location'] is not None:
            self.signer = Sign_0_21(privateKeyID=options['key'] ,publicKeyLocations=[options['key_location']], passphrase=options['passphrase'], gpgbin=options['gpgbin'])
        else:
            self.signer = None


        # node-based signing
        #if not self.signer:
        #    raise Exception("Failed to load document signer, please check configuration.")

    def start(self):
        resumption_token = None

        currentTombstone = self._build_tombstone()

        while True:
            if len(_debug_ID):
            	currentTombstone["replaces"] = [_debug_ID]
            	break

            idRequest = self.get_document_ids(resumption_token)

            currentTombstone["replaces"].extend(idRequest['ids'])

            # abide batch request
            if self.options["batch"] <= len(currentTombstone["replaces"]):
                self.sign_and_send(currentTombstone)

                currentTombstone = self._build_tombstone()


            if('resumption_token' in idRequest):
                resumption_token = idRequest['resumption_token']
            else:
                break


        if len(currentTombstone["replaces"]):
            self.sign_and_send(currentTombstone)
        else:
            print "No documents found to delete"


    def get_document_ids(self, resumption_token = None):
        params = {
            'identity': self.identity,
            'ids_only': True
        }

        if resumption_token:
            params['resumption_token'] = resumption_token

        url = self.server+'/slice?'+urlencode(params)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)

        jsonResult = json.load(response)

        result = {
            'ids': (x['doc_ID'] for x in jsonResult['documents'])
        }

        if('resumption_token' in jsonResult):
            result['resumption_token'] = jsonResult['resumption_token']
            print "sleeping for 20 seconds"
            time.sleep(20)

        return result

    def _build_tombstone(self, docID = None):
        tombstone = copy.deepcopy(_TOMBSTONE_DOCUMENT)

        if docID:
            if(isinstance(docID, list)):
                tombstone["replaces"].extend(docID)
            else:
                tombstone["replaces"].append(docID)

        tombstone["identity"].update({
            "submitter": self.options['submitter']
        })

        if(self.signer):
            tombstone["identity"].update({
                "signer": self.options['signer']
            })

        return tombstone

    def sign_and_send(self, document):
        signed = self.sign_document(document)
        self.upload_documents([signed])
        #self.upload_documents_oauth([signed])

    def sign_document(self, document):

        if(self.signer):
            return self.signer.sign(document)

        return document

    def upload_documents_oauth(self, docs):

        if len(docs) == 0: return

        print "Batch sending", len(docs), "documents"

        data = json.dumps({'documents':docs}, indent=4)

        print data

        publish_url = self.server+'publish'

        consumer = oauth.Consumer(key=_consumer["key"], secret=_consumer["secret"])
        token = oauth.Token(key=_token["key"], secret=_token["secret"])
        # Create our client.
        client = oauth.Client(consumer, token=token)
        # we only need to do this because Sandbox uses a self-signed SSL cert that is untrusted. This should not be needed on production.
        #client.disable_ssl_certificate_validation = True
        try:
            print "Authenticating..."
            resp, content = client.request(
                                "https://%s/auth/oauth_verify" % options['host'],
                                "POST",
                                body="",
                                headers={"Content-Type": "application/json"}
                            )
            content_json = json.loads(content)
            if content_json['status'] == 'Okay':
                print "status : Okay"
                resp, content = client.request(
                            publish_url,
                            "POST",
                            body=data,
                            headers={"Content-Type": "application/json; charset=utf-8"}
                        )
                content_json = json.loads(content)


            else:
                print "Error authenticating with the Learning Registry."
                print "status:", content_json['status']
                if 'detail' in content_json:
                    print "detail:", content_json['detail']


            print content

        except Exception, e:
            print e


    def upload_documents(self, docs):

        if len(docs) == 0: return

        print "Batch sending", len(docs), "documents"

        try:
            data = json.dumps({'documents':docs}, indent=4)

            print data

            publish_url = self.server+'publish'

            if self.options["user"] is not None and self.options["passwd"] is not None:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, publish_url, self.options["user"], self.options["passwd"])
                auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(auth_handler)
                urllib2.install_opener(opener)

            request = urllib2.Request(publish_url,data,{'Content-Type':'application/json; charset=utf-8'})
            response = urllib2.urlopen(request)

            result = response.read()

            print result

        except urllib2.HTTPError as er:
            print er.read()


if __name__== "__main__":

    parser = ArgumentParser()
    parser.add_argument("-n", dest="host",
                      help="The LR node host to publish to (defaults to test node)", default="sandbox.learningregistry.org")

    parser.add_argument("-i", dest="identity",
                      help="[REQUIRED] The identity of records to be removed", required=True)

    parser.add_argument("-o", dest="submitter",
                      help="[REQUIRED] Person or organization name of submitter", required=True)

    parser.add_argument("-s", dest="signer",
                      help="[REQUIRED] Person or organization name of signer", required=True)


    parser.add_argument('--key', help='PGP Private Key ID', default=None)
    parser.add_argument('--key_location', help='Location the PGP Public Key can be downloaded from', default=None)
    parser.add_argument('--passphrase', help='Passphrase for PGP Private Key', default=None)
    parser.add_argument('--gpgbin', help='Path to GPG binary', default="gpg")
    parser.add_argument('--user',help="Username for basic auth", default=None)
    parser.add_argument('--passwd',help="Password for basic auth", default=None)

    parser.add_argument('--batch', type=int, help="Number of documents to batch/delete at a time (default = 100)",default=100)

    parser.add_argument('--config', help="Configuration file (overrides arguments)",default=None)

    options = vars(parser.parse_args())


    if(options["config"] is not None):
        config = ConfigParser.ConfigParser()
        config.read(options["config"])

        options.update(config._sections["signature"])


    massDelete = MassDelete(options)
    massDelete.start()

