from lr.tests import *

class TestOaiPmhsController(TestController):

    def test_index(self):
        response = self.app.get(url('OAI-PMHS'))
        # Test response...

    def test_index_as_xml(self):
        response = self.app.get(url('formatted_OAI-PMHS', format='xml'))

    def test_create(self):
        response = self.app.post(url('OAI-PMHS'))

    def test_new(self):
        response = self.app.get(url('new_OAI-PMH'))

    def test_new_as_xml(self):
        response = self.app.get(url('formatted_new_OAI-PMH', format='xml'))

    def test_update(self):
        response = self.app.put(url('OAI-PMH', id=1))

    def test_update_browser_fakeout(self):
        response = self.app.post(url('OAI-PMH', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.delete(url('OAI-PMH', id=1))

    def test_delete_browser_fakeout(self):
        response = self.app.post(url('OAI-PMH', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('OAI-PMH', id=1))

    def test_show_as_xml(self):
        response = self.app.get(url('formatted_OAI-PMH', id=1, format='xml'))

    def test_edit(self):
        response = self.app.get(url('edit_OAI-PMH', id=1))

    def test_edit_as_xml(self):
        response = self.app.get(url('formatted_edit_OAI-PMH', id=1, format='xml'))
