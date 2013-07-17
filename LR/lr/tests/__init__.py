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
from webtest import TestApp,AppError
from datetime import datetime
import pylons.test
import logging, wsgi_intercept
from nose.tools import raises
log = logging.getLogger(__name__)
__all__ = ['environ', 'url', 'TestController']
time_format = '%Y-%m-%d %H:%M:%SZ'
# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}
class OptionsTestApp(TestApp):
    def options(self,url,headers):
        return self._gen_request(method='OPTIONS', url=url,headers=headers)        
class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = OptionsTestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)
        self.from_date = datetime(1990,1,1).isoformat() + "Z"
        self.controllerName = None
        def get_wsgiapp():
            return wsgiapp
        wsgi_intercept.add_wsgi_intercept('localhost', 80, get_wsgiapp)
        wsgi_intercept.add_wsgi_intercept('127.0.0.1', 80, get_wsgiapp)


    def test_error(self):       
        resp = self.app.get(url(controller='foo'), status=404)
        assert resp.headers['Content-Type'] == 'text/html; charset=utf-8'

    def test_options(self):
        if self.controllerName is not None:
            res = self.app.options(url(controller=self.controllerName),headers={'origin':'http://foo.bar'})
            assert res.headers['Access-Control-Allow-Origin'] == 'http://foo.bar'
            assert res.headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
            assert res.headers['Access-Control-Max-Age'] == '1728000'
            assert res.headers['Access-Control-Allow-Headers'] == 'Content-Type,Origin,Accept,Authorization'
