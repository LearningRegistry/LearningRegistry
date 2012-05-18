from lr.tests import *
import urlparse
import couchdb
from pylons import config
class TestRegisterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='register', action='index'))
        assert response.headers['Content-Type'] == 'text/html;charset=utf-8'
    def test_create(self):
    	destUrl = config['couchdb.url']
    	response = self.app.post(url(controller="register",action="create"),params={"destUrl":destUrl,'contact':'joe@example.com'})
    	assert response.status_int == 200
    def test_create_with_user(self):
        destUrl = config['couchdb.url']
        response = self.app.post(url(controller="register",action="create"),params={"destUrl":destUrl,'username':"testUser","password":"password",'contact':'joe@example.com'})
        assert response.status_int == 200        
        s= couchdb.Server(config['couchdb.url'])
        db = s[config['couchdb.db.node']]
        creds = db['access_credentials']
        destinationURL = urlparse.urljoin(destUrl.strip(),"incoming")
        creds=creds['passwords'][destinationURL]
        assert creds['username'] == 'testUser'
        assert creds['password'] == 'password'
    def test_create_invalid_url(self):
    	response = self.app.post(url(controller="register",action="create"),params={"destUrl":"123"}, status=400)
    	assert response.status_int == 400