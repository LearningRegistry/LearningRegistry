from lr.tests import *

class TestRegisterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='register', action='index'))
        assert response.headers['Content-Type'] == 'text/html;charset=utf-8'
    def test_create(self):
    	response = self.app.post(url(controller="register",action="create"),params={"destUrl":"http://localhost:5984/resource_data"})
    	assert response.status_int == 200
    def test_create_invalid_url(self):
    	response = self.app.post(url(controller="register",action="create"),params={"destUrl":"123"}, status=400)
    	assert response.status_int == 400