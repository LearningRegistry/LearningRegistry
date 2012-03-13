import logging
from  iso8601 import parse_date
from datetime import datetime
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
    def _getView(self,view='_all_docs',keys=[], includeDocs=True,startKey=None,endKey=None):
        args = {'include_docs':includeDocs}
        if len(keys) > 0:
            args['keys'] = keys
        args['reduce']=False
        args['stale'] = appConfig['couchdb.stale.flag']
        args['limit']=10
        if startKey is not None:
            args['startkey'] = startKey
        if endKey is not None:
            args['endkey'] = endKey
        db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])        
        log.debug(db_url)
        view = h.getView(database_url=db_url,view_name=view,documentHandler=h.document,**args)
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
        for d in self._streamList(self._getView(keys=ids,includeDocs=includeDocs),lambda d: json.dumps(d)):
            yield d
        yield base[index:]
    def _convertDateTime(self,dt):
        if isinstance(dt,str):
            dt = parse_date(dt)
        dt = dt - datetime(1970,1,1)
        return dt.total_seconds()
    def _processRequest(self,startKey, endKey,urlBase):
        yield '{"documents":['        
        def processFeed(item):            
            for piece in self._getBaseResult(item,ids=[item['id']]):
                yield piece            
        for d in self._streamList(self._getView(urlBase,startKey=startKey,endKey=endKey,includeDocs=False),processFeed):
            yield d        
        yield ']}'        
    def _orderParmaByView(self,params,view):
        startKey=[]
        endKey=[] 
        def populateTs():
            if 'from' in params:
                startKey.append(self._convertDateTime(params['from']))
            else:
                startKey.append(self._convertDateTime(datetime.min))
            if 'until' in params:
                endKey.append(self._convertDateTime(params['until']))
            else:
                endKey.append(self._convertDateTime(datetime.max))                
        def populateDiscriminator():
            if 'discriminator' in params:
                startKey.append(params['discriminator'])
                endKey.append(params['discriminator']+'\ud7af')
            else:
                startKey.append('')
                endKey.append('\ud7af')            
        def populateResource():
            if 'resource' in params:
                startKey.append(params['resource'])
                endKey.append(params['resource']+'\ud7af')
            else:
                startKey.append('')
                endKey.append('\ud7af')       
        funcs = {
            "discriminator":populateDiscriminator,
            'resource':populateResource,
            'ts':populateTs
        }       
        queryOrderParts = view.split('-by-')
        aggregate = queryOrderParts[0]
        queryParams= queryOrderParts[1].split('-')       
        for q in queryParams:
            funcs[q]
        funcs[aggregate]
        return startKey if len(startKey) > 0 else None, endKey if len(endKey) > 0 else None

    def get(self, dataservice="",view=''):
        """GET /extract/id: Show a specific item"""        
        urlBase = "_design/{0}/_view/{1}".format(dataservice,view)        
        startKey, endKey = self._orderParmaByView(request.params,view)
        log.debug('Start Key: {0}; End Key: {1}'.format(startKey,endKey))
        return self._processRequest(startKey,endKey,urlBase)