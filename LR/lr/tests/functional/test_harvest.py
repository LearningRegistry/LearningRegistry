from lr.tests import *
import logging
log = logging.getLogger(__name__)
class TestHarvestController(TestController):

    def test_index(self):
 #       try:
          response = self.app.get(url(controller='harvest', action='index', id='getrecord',params='request_Id=00b4c7a8cd5d427e9be2316f7414efb2&by_doc_ID=True'}))
#        except Exception as err:
#          pass 
        # Test response...

    def test_create(self):
        response = self.app.post(url(controller='harvest', action='create'))

'''    def test_new(self):
        try:
          response = self.app.get(url('new_harvest'))
        except Exception as ex:
          print ex

    def test_update(self):
        response = self.app.put(url('harvest', id=1))

    def test_update_browser_fakeout(self):
        response = self.app.post(url('harvest', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.delete(url('harvest', id=1))

    def test_delete_browser_fakeout(self):
        response = self.app.post(url('harvest', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('harvest', id=1))

    def test_show_as_xml(self):
        response = self.app.get(url('formatted_harvest', id=1, format='xml'))

    def test_edit(self):
        response = self.app.get(url('edit_harvest', id=1))'''
