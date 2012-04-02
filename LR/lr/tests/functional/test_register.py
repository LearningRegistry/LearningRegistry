from lr.tests import *

class TestRegisterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='register', action='index'))
        assert response.headers['Content-Type'] == 'text/html;charset=utf-8'
    def test_create(self):
    	response = self.app.post(url(controller="register",action="create"),params={"destUrl":"123"})
    	assert response.status_int == 200
