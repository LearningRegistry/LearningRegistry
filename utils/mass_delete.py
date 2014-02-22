#!/usr/bin/env python

import copy, re, urllib2, json, ConfigParser
from urllib import urlencode
from argparse import ArgumentParser
from pprint import pprint
from LRSignature.sign.Sign import Sign_0_21


_TOMBSTONE_DOCUMENT = {
    "replaces": [],
    "TOS": {
        "submission_TOS": "http://www.learningregistry.org/tos/cc0/v0-5/"
    },
    "active": False,
    "doc_type": "resource_data",
    "doc_version": "0.49.0",
    "identity": {
        "curator": "",
        "owner": "",
        "submitter": "",
        "signer": "",
        "submitter_type": "agent"
    },
    "payload_placement": "none",
    "resource_data_type": "metadata"
}

class MassDelete:

    def __init__(self, options):
        self.options = options

        self.server = 'http://'+options['host']+'/'
        self.identity = options['identity']

        if options['key'] is not None and options['key_location'] is not None:
            self.signer = Sign_0_21(privateKeyID=options['key'] ,publicKeyLocations=[options['key_location']], passphrase=options['passphrase'], gpgbin=options['gpgbin'])
        else:
            self.signer = None


        if not self.signer:
            raise Exception("Failed to load document signer, please check configuration")

    def start(self):
        resumption_token = None

        currentTombstone = self._build_tombstone()

        while True:
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

        return result

    def _build_tombstone(self, docID = None):
        tombstone = copy.deepcopy(_TOMBSTONE_DOCUMENT)

        if docID:
            if(isinstance(docID, list)):
                tombstone["replaces"].extend(docID)
            else:
                tombstone["replaces"].append(docID)

        tombstone["identity"].update({
            "submitter": self.options['submitter'],
            "signer": self.options['signer']
        })

        return tombstone

    def sign_and_send(self, document):
        signed = self.sign_document(document)
        self.upload_documents([signed])

    def sign_document(self, document):

        if(self.signer):
            return self.signer.sign(document)

        return document

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


    parser.add_argument('--key', help='PGP Private Key ID')
    parser.add_argument('--key-location', help='Location the PGP Public Key can be downloaded from')
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

