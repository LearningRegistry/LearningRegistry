#!/usr/bin/env python

import copy, re, urllib, urllib2, json, ConfigParser, time, base64, subprocess
from argparse import ArgumentParser
from pprint import pprint

class ChangePass:

    def __init__(self, options):
        self.options = options

        self.server = options['protocol']+'://'+options['host']+':'+options['couch_port']
        self.default_pass = options['default_pass']

    def start(self):
        usersList = self._list_users()

        for id in usersList['users']:
            if id[:16] == 'org.couchdb.user':
                email = id[17:len(id)]
                userData = self._get_user(id)

                # if a publishing password is set, skip this user
                passSet = userData.get('password_sha', None)

                if passSet is None:
                    print "Changing password for " + email
                    self._change_pass(userData)
                else:
                    print "Has password_sha, skipping changing password for " + email

    def _list_users(self):
        url = self.server+'/_users/_all_docs'

        jsonResult = self._request(url)

        result = {
            'users': (x['id'] for x in jsonResult['rows'])
        }

        return result

    def _get_user(self, user_id):
        url = self.server+'/_users/'+user_id

        jsonResponse = self._request(url)

        return jsonResponse

    def _request(self, url, post_data = '', match_header = ''):
        hdr = {"Accept": "application/json",
              "User-Agent": "Mozilla/5.0",
              "Referer": url}

        try:
            if post_data != '':
                #data = urllib.urlencode(post_data)
                request = urllib2.Request(url, post_data, headers=hdr)
                request.add_header("Content-Type", "multipart/form-data")

            else:
                request = urllib2.Request(url, headers=hdr)
                request.add_header("Content-Type", "application/json")

            base64string = base64.b64encode('%s:%s' % (self.options["couch_admin"], self.options["couch_pass"]))
            request.add_header("Authorization", "Basic %s" % base64string)

            if match_header != '':
                request.add_header("If-Match", match_header)

            response = urllib2.urlopen(request)
            data = response.read()
            return json.loads(data)

        except urllib2.HTTPError as er:
            print er.read()
            return False

    # could not get proper headers/options sent to couch via urllib, so reverted to just curl
    def _change_pass(self, userData):
        curlOptions = '-X PUT ' + self.options['protocol'] + '://' + self.options['couch_admin'] + ':'+ self.options['couch_pass'] + '@' + self.options['host']+':' + self.options['couch_port'] + '/_users/' + userData['_id']
        curlOptions = curlOptions + ' -H "Accept: application/json" -H "Content-Type: application/json"'
        curlOptions = curlOptions + ' -H "If-Match: ' + userData['_rev'] + '"'

        # strip out the password
        userData.pop("password_sha", None)

        # add the default pass
        userData['password'] = self.default_pass

        curlOptions = curlOptions + " -d '" + json.dumps(userData) + "'"
        print curlOptions

        print subprocess.Popen("curl "+curlOptions, shell=True, stdout=subprocess.PIPE).stdout.read()



if __name__== "__main__":

    parser = ArgumentParser()
    parser.add_argument("--host", dest="host",
                      help="The LR node host to publish to (defaults to test node)", default="localhost")

    parser.add_argument("--protocol", dest="protocol",
                      help="Protocol to use: http or https (defaults to http)", default="http")

    parser.add_argument("--couch-admin", dest="couch_admin",
                      help="couchdb admin user (defaults to admin)", default="admin")

    parser.add_argument("--couch-pass", dest="couch_pass",
                      help="couchdb admin password (defaults to password)", default="password")

    parser.add_argument("--couch-port", dest="couch_port",
                      help="port couch is running on", default="5984")

    parser.add_argument("--default-pass", dest="default_pass",
                      help="New default password for users", default="password")

    options = vars(parser.parse_args())

    changePass = ChangePass(options)
    changePass.start()

