from lr.lib.helpers import *
import base64


def test_getBasicAuthHeaderFromURL_no_auth():
    url = "http://learningregistry.org"
    auth = getBasicAuthHeaderFromURL(url)
    assert auth == {}


def test_getBasicAuthHeaderFromURL():
    url = "http://user:password@learningregistry.org"
    base64_enc = base64.encodestring("user:password").replace("\n", "")
    auth = getBasicAuthHeaderFromURL(url)
    assert "Authorization" in auth
    assert ("Basic %s" % base64_enc) == auth['Authorization']
