from lr.tests import *

class TestPublisherController(TestController):
    def __init__(self, *args, **kwargs):
        TestController.__init__(self,*args,**kwargs)
        self.controllerName = "publish"
    def test_index(self):
        pass
