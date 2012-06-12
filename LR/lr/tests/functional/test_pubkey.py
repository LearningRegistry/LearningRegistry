from lr.tests import *

class TestPubkeyController(TestController):

    def test_index(self):
        response = self.app.get('/pubkey')
        # Test response...

    def test_create(self):
        response = self.app.post('/pubkey')
