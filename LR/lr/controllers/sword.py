import logging
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest
from lr.lib.base import BaseController, render
import lr.model as m
from lr.lib.harvest import harvest
import json
log = logging.getLogger(__name__)

class SwordError(Exception):
    def __init__(self,value):
      self.value = value
    def __str__(self):
      return repr(self.value)
class SwordController(BaseController):
    def __init__(self):
        self.h = harvest()
    def __before__(self):
        response.headers['content-type'] = 'application/atom+xml;charset=utf-8'      
        self.parse_params()
    def index(self): 
        c.collectino_url = 'http://' + request.host + '/obtain/'
        return render('sword.mako')	
    def parse_params(self):
        c.user_agent = request.headers['user-agent']
        c.no_op = False
        c.verbose = False
        if request.headers.has_key('X-On-Behalf-Of'):
            c.on_behalf_of = request.headers['X-On-Behalf-Of']
        if request.headers.has_key('X-Verbose'):
            c.verbose = request.headers['X-Verbose']
        if request.headers.has_key('X-No-Op'):
            c.no_op = request.headers['X-No-Op']
        c.tos_url = m.base_model.appConfig['tos.url']
        c.generator_url = 'http://' + request.host + '/sword'
    def create(self):		
        if c.no_op:
            result = {'OK':True}
            c.doc = {'doc_ID':12345}
        else:
            result = m.publish(json.loads(request.body))
        if result['OK']:
            c.content_url = 'http://' + request.host + '/obtain/'+result['doc_ID']
            c.doc = self.h.get_record(result['doc_ID'])			
            return render('sword-publish.mako')    
        else:
            raise SwordError(result['error'])
