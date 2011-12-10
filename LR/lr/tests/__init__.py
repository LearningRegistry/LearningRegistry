"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp
from datetime import datetime
import pylons.test
import logging
log = logging.getLogger(__name__)
__all__ = ['environ', 'url', 'TestController']
time_format = '%Y-%m-%d %H:%M:%SZ'
# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}
class LRTestApp(TestApp):
	def options(self,url):
		return self._gen_request('OPTIONS', url)		

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
    	self.controllerName = None
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = LRTestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)
        self.from_date = datetime(1990,1,1).isoformat() + "Z"
        self.until_date = datetime.utcnow().isoformat()+"Z"
       
    def test_options(self):
    	if self.controllerName:
    		res = self.app.options(url(controller=self.controllerName))
    		assert res.headers['Access-Control-Allow-Origin'] == '*'
    		assert res.headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
    		assert res.headers['Access-Control-Max-Age'] == '1728000'
