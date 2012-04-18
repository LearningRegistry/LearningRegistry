import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from lr.model.node_status import NodeStatusModel
from lr.model import NodeConnectivityModel
log = logging.getLogger(__name__)
import uuid
import urllib2
import httplib
class RegisterController(BaseController):
    def __before__(self):
        response.headers['Content-Type'] = 'text/html;charset=utf-8'
    def _publishConnection(self,destUrl):
        connectionInfo = {
           "doc_type": "connection_description",
           "gateway_connection": False,
           "connection_id": uuid.uuid1().hex,
           "destination_node_url": destUrl,
           "doc_version": "0.10.0",
           "source_node_url": request.host_url,
           "active": True,
           "doc_scope": "node"
        }       
        try:
            urllib2.urlopen(destUrl)
            conn = NodeConnectivityModel(connectionInfo)
            result = conn.save()
            if result["OK"]:
                return "Your end point was successfully registered"
            else:
                return result['error']
        except httplib.HTTPException:
            abort(400,"Invalid destination URL")
        except ValueError:
            abort(400, "Invalid URL format")
    def index(self):
        # Return a rendered template
        #return render('/register.mako')
        # or, return a string
        def get():
            return render("register.mako")
        def post():
            return "POST"
        switch = {
            "GET":get,
            "POST":post
        }
        return switch[request.method]()
    def create(self):

        return self._publishConnection(request.POST['destUrl'])
