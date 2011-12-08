import logging
import urlparse
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest
from lr.lib.base import BaseController, render
import lr.model as m
from lr.controllers.publish import PublishController
from lr.lib.harvest import harvest
import json
from lr.model import LRNode as sourceLRNode
from pylons.decorators.rest import restrict
log = logging.getLogger(__name__)

class SwordError(Exception):
    def __init__(self,value):
      self.value = value
    def __str__(self):
      return repr(self.value)
class SwordserviceController(PublishController):
    def __init__(self):
        self.h = harvest()
    def __before__(self):
        response.headers['Content-Type'] = 'application/atom+xml;charset=utf-8'
        self.parse_params()
    def index(self): 
        c.collection_url = urlparse.urljoin(self.baseUrl,'swordpub')
        if sourceLRNode.nodeDescription.node_name is not None:
            c.node_name = sourceLRNode.nodeDescription.node_name
        else:
            c.node_name = sourceLRNode.nodeDescription.node_id
        c.node_description = sourceLRNode.nodeDescription.node_description
        if sourceLRNode.communityDescription.community_name is not None:                    
            c.community_name = sourceLRNode.communityDescription.community_name
        else:
            c.community_name = sourceLRNode.communityDescription.community_id
        return render('sword.mako')	
    def parse_params(self):
        c.user_agent = request.headers['user-agent']
        c.no_op = False
        c.verbose = False
        #for some reason request.url has an extra '/' in it
        lastSlash = request.url.rfind('/')        
        self.baseUrl = request.url[:lastSlash]+request.url[lastSlash+1:]
        if request.headers.has_key('X-On-Behalf-Of'):
            c.on_behalf_of = request.headers['X-On-Behalf-Of']
        if request.headers.has_key('X-Verbose'):
            c.verbose = request.headers['X-Verbose']
        if request.headers.has_key('X-No-Op'):
            c.no_op = request.headers['X-No-Op']
        c.tos_url = m.base_model.appConfig['tos.url']
        c.generator_url = self.baseUrl
    @restrict("POST")
    def create(self):		
        log.debug(request.body)
        if c.no_op:
            result = {'OK':True}
            c.doc = {'doc_ID':12345}
        else:
            result = self._publish(json.loads(request.body))
        if result['OK']:
            c.content_url = urlparse.urljoin(self.baseUrl,'obtain') + '?request_id=%s&by_doc_ID=true' % result['doc_ID']
            c.doc = self.h.get_record(result['doc_ID'])			
            return render('sword-publish.mako')    
        else:
            raise SwordError(result['error'])
