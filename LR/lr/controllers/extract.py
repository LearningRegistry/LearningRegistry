import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.model.base_model import appConfig
from lr.lib.base import BaseController, render
import json
import ijson
from urllib2 import urlopen
import lr.lib.helpers as h
log = logging.getLogger(__name__)

class ExtractController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('extract', 'extract')
    def _getView(self,view='_all_docs',keys=[], includeDocs=True):
        args = {'include_docs':includeDocs}
        if len(keys) > 0:
            args['keys'] = keys
        args['limit'] = 10
        db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])
        if includeDocs:
            documentHandler = lambda d: d['doc']
        else:
            documentHandler = lambda d: d['id']
        view = h.getView(database_url=db_url,view_name=view,documentHandler=documentHandler,**args)
        return view
    def _streamList(self,data,dataHandler):
        first = True
        for item in data:
            if not first:
                yield ",\n"
            else:
                first = False                        
            for d in  dataHandler(item):
                yield d
    def _getBaseResult(self,data={},ids=[], includeDocs=True):
        base =  json.dumps({
                        "result_data": data,
                        "supplemental_data" : {},
                        "resource_data": []        
                })
        index = base.rfind('[') + 1
        yield base[:index]
        for d in self._streamList(self._getView(includeDocs=False),json.dumps):
            yield d
        yield base[index:]
    def show(self, id, format='html'):
        """GET /extract/id: Show a specific item"""
        yield '{"documents":['
        first = True
        def processFeed(item):            
            for piece in self._getBaseResult():
                yield piece            
        for d in self._streamList(xrange(10),processFeed):
            yield d        
        yield ']}'