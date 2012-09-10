from lr.tests import *
from lr.util import decorators
from lr.lib import oauth, bauth

from pylons import config, request
import couchdb, oauth2,urlparse, json

# rpdb2.start_embedded_debugger("password")



class TestAuthController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self, *args, **kwargs)

        self.oauth_info = {
                "name": "tester@example.com",
                "full_name": "Joe Tester"
        }

        self.oauth_user = {
           "_id": "org.couchdb.user:{0}".format(self.oauth_info["name"]),
           "type": "user",
           "name": self.oauth_info["name"],
           "roles": [
               "browserid"
           ],
           "browserid": True,
           "oauth": {
               "consumer_keys": {
                   self.oauth_info["name"] : "ABC_consumer_key_123"
               },
               "tokens": {
                   "node_sign_token": "QWERTY_token_ASDFGH",
               }
           },
           "lrsignature": {
               "full_name": self.oauth_info["full_name"]
           }
        }

        self.bauth_user = {
          "name": "mrbasicauth",
          "password": "ABC_123"
        }

    # def test_index(self):
    #     response = self.app.get(url(controller='oauth', action='index'))
    #     # Test response...

    @decorators.OAuthRequest(path="/auth/oauth_verify")
    def test_oauth_verify(self):

        response = self.app.get(self.oauth.path, headers=self.oauth.header, extra_environ=self.oauth.env)

        res = response.json
        assert res["status"] == oauth.status.Okay, "Should be Okay"
        assert res["user"]["name"] == self.oauth_info["name"], "Email Address Does not match"
        assert res["user"]["lrsignature"]["full_name"] == self.oauth_info["full_name"], "Full Name Does not match"

    @decorators.BasicAuthRequest(bauth_user_attrib="bauth_user", bauth_info_attrib="bauth")
    def test_basic_verify(self):

        response = self.app.get("/auth/basic_verify", headers=self.bauth.header)

        res = response.json
        assert res["status"] == bauth.status.Okay, "Should be Okay"
        assert res["user"]["name"] == self.bauth.username, "Username Does not match"

    @decorators.BasicAuthRequest(bauth_user_attrib="bauth_user", bauth_info_attrib="bauth")
    def test_basic_auth_fail(self):
        test_headers = {}
        test_headers['Authorization'] = "Basic 123564"
        self.app.get("/auth/basic_verify", headers=test_headers, status=401)
