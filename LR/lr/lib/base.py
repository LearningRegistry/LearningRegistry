"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_mako as render
from pylons import response,request
class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        response.headers['content-type'] = 'application/json;charset=utf-8'
        self.setOrigin()
        return WSGIController.__call__(self, environ, start_response)
    def options(self):        
    	response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    	response.headers['Access-Control-Max-Age'] = '1728000'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Origin,Accept,Authorization'
    def setOrigin(self):
        if 'origin' in request.headers:
           response.headers['Access-Control-Allow-Origin'] = request.headers['origin']
