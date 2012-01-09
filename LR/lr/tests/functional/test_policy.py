from lr.tests import *

class TestPolicyController(TestController):

    def test_index(self):
        response = self.app.get(url('policy'))
        # Test response...

    def test_index_as_xml(self):
        response = self.app.get(url('formatted_policy', format='xml'))

    def test_create(self):
        response = self.app.post(url('policy'))

    def test_new(self):
        response = self.app.get(url('new_policy'))

    def test_new_as_xml(self):
        response = self.app.get(url('formatted_new_policy', format='xml'))

    def test_update(self):
        response = self.app.put(url('policy', id=1))

    def test_update_browser_fakeout(self):
        response = self.app.post(url('policy', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.delete(url('policy', id=1))

    def test_delete_browser_fakeout(self):
        response = self.app.post(url('policy', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('policy', id=1))

    def test_show_as_xml(self):
        response = self.app.get(url('formatted_policy', id=1, format='xml'))

    def test_edit(self):
        response = self.app.get(url('edit_policy', id=1))

    def test_edit_as_xml(self):
        response = self.app.get(url('formatted_edit_policy', id=1, format='xml'))
