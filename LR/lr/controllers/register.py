import browserid, json
import logging
import urlparse
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from lr.model.node_status import NodeStatusModel
from lr.model import NodeConnectivityModel,LRNode as sourceLRNode
log = logging.getLogger(__name__)
import uuid
import urllib2
import httplib

class RegisterController(BaseController):
    def __before__(self):
        response.headers['Content-Type'] = 'application/json;charset=utf-8'
    def _publishConnection(self,destUrl,username,password,contact):
        connectionInfo = {
           "doc_type": "connection_description",
           "gateway_connection": False,
           "connection_id": uuid.uuid1().hex,
           "destination_node_url": destUrl,
           "doc_version": "0.10.0",
           "source_node_url": request.host_url,
           "active": True,
           "doc_scope": "node",
           "X_contact": contact
        }       
        try:
            urllib2.urlopen(destUrl)
            conn = NodeConnectivityModel(connectionInfo)
            result = conn.save()
            destinationURL = urlparse.urljoin(destUrl.strip(),"incoming")
            if bool(username) and bool(password):
                sourceLRNode.addDistributeCredentialFor(destinationURL,username,password)
            if result["OK"]:
                return json.dumps({"status":"okay", "msg":"Your end point was successfully registered"})
            else:
                return json.dumps({"status":"error", "msg":result['error']})

        except httplib.HTTPException:
            return abort(400, "Invalid destination URL")
        except ValueError:
            abort(400, "Invalid URL format")
        except:
            import sys
            exc_type, exc_val = sys.exc_info()[:2]
            abort(400, "{0}: {1}".format(exc_type, exc_val))

    def index(self):
        # Return a rendered template
        #return render('/register.mako')
        # or, return a string
        def get():
            response.headers['Content-Type'] = 'text/html;charset=utf-8'
            return render("register.mako")
        def post():
            return "POST"
        switch = {
            "GET":get,
            "POST":post
        }
        return switch[request.method]()

    def create(self):
        username = None
        password = None
        destination = None
        contact = None
        if 'username' in request.POST:
            username = request.POST['username']
        if 'password' in request.POST:
            password = request.POST['password']
        if 'destUrl' in request.POST:
            destination = request.POST['destUrl']
        if 'contact' in request.POST:
            contact = request.POST['contact']

        return self._publishConnection(destination,username,password,contact)

    def verify(self):
        data = {'status': 'error'}
        if request.method == 'POST' and "assertion" in request.POST:
            data = browserid.verify(request.POST["assertion"], request.host_url)
        return json.dumps(data)
