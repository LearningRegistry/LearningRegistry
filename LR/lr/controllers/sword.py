import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest
from lr.lib.base import BaseController, render
import lr.model as m
from lr.lib.harvest import harvest
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
    def index(self): 
        # Return a rendered template
        #return render('/sword.mako')
        # or, return a string
        return render('sword.mako')
    def create(self):
        c.user_agent = request.headers['user-agent']
        c.no_op = False
        c.verbose = False
        if request.headers.has_key('X-Verbose'):
          c.verbose = request.headers.has_key('X-Verbose')
          log.debug(c.verbose)           
        if request.headers.has_key('X-No-Op') and request.headers['X-No-Op'] == True:
          c.no_op = True
          result = {'OK':True}
          c.doc = {'doc_ID':12345}
        else:
          result = m.publish(request.body)
          c.content_url = 'http://' + request.host + '/obtain/'+result['doc_ID']
          c.generator_url = 'http://' + request.host + '/sword'
          log.debug(request.host)
          c.doc = self.h.get_record(result['doc_ID'])
        if result['OK']:
            return render('sword-publish.mako')    
        else:
            raise SwordError(result['error'])
