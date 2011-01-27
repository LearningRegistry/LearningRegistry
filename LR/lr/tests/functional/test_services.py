from lr.tests import *

class TestServicesController(TestController):

    def test_index(self):
        response = self.app.get(url('services'))
        # Test response...

    def test_index_as_xml(self):
        response = self.app.get(url('formatted_services', format='xml'))

    def test_create(self):
        response = self.app.post(url('services'))

    def test_new(self):
        response = self.app.get(url('new_services'))

    def test_new_as_xml(self):
        response = self.app.get(url('formatted_new_services', format='xml'))

    def test_update(self):
        response = self.app.put(url('services', id=1))

    def test_update_browser_fakeout(self):
        response = self.app.post(url('services', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.delete(url('services', id=1))

    def test_delete_browser_fakeout(self):
        response = self.app.post(url('services', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('services', id=1))

    def test_show_as_xml(self):
        response = self.app.get(url('formatted_services', id=1, format='xml'))

    def test_edit(self):
        response = self.app.get(url('edit_services', id=1))

    def test_edit_as_xml(self):
        response = self.app.get(url('formatted_edit_services', id=1, format='xml'))
