from lr.controllers.publish import PublishController, _continue_if_missing_oauth, _no_abort
from lr.lib import signing, oauth, bauth, helpers as h
from lr.lib.base import BaseController, render
from lr.lib.harvest import harvest
from lr.model import LRNode as sourceLRNode
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest
from pylons.decorators.rest import restrict
import json
import logging
import lr.model as m
import urlparse

log = logging.getLogger(__name__)

class SwordError(Exception):
    def __init__(self,value):
      self.value = value
    def __str__(self):
      return repr(self.value)

__service_doc = None
def _service_doc(recache=False):
    def get_service_doc():
        global __service_doc
        
        if not __service_doc or recache:
            __service_doc = h.getServiceDocument(m.base_model.appConfig["lr.sword.docid"])
        return __service_doc
    return get_service_doc

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
        if 'user-agent' in request.headers:
            c.user_agent = request.headers['user-agent']
        else:
            c.user_agane = ""
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
    @oauth.authorize("oauth-sign", _service_doc(True), roles=None, mapper=signing.lrsignature_mapper, post_cond=_no_abort)
    @bauth.authorize("oauth-sign", _service_doc(), roles=None, pre_cond=_continue_if_missing_oauth, realm="Learning Registry")
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
