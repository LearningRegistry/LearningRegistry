import logging
import StringIO
from  iso8601 import parse_date
from datetime import datetime
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from lr.model.base_model import appConfig
from lr.lib.base import BaseController, render
import json
import ijson
import math
from urllib2 import urlopen,HTTPError
import lr.lib.helpers as h
log = logging.getLogger(__name__)
import couchdb
class ExtractController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('extract', 'extract')
    def _getView(self,view='_all_docs',keys=[], includeDocs=True,startKey=None,endKey=None):
        args = {'include_docs':includeDocs}
        if len(keys) > 0:
            args['keys'] = keys
        args['reduce']= False
        args['stale'] = appConfig['couchdb.stale.flag']
        if startKey is not None:
            args['startkey'] = startKey
        if endKey is not None:
            args['endkey'] = endKey
        db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])        
        view = h.getResponse(database_url=db_url,view_name=view,**args)
        return view
    def _convertDateTime(self,dt):
        try:
            epoch = parse_date("1970-01-01T00:00:01Z")        
            if isinstance(dt, str) or isinstance(dt,unicode):
                dt = parse_date(dt)
            dt = dt - epoch
            return int(math.floor(dt.total_seconds()))
        except:
            abort(500,"Invalid Date Format")
    def _processRequest(self,startKey, endKey,urlBase, includeDocs=True):
        def streamResult(resp):
            CHUNK_SIZE=1024
            data = resp.read(CHUNK_SIZE)
            while len(data) > 0:
                yield data
                data = resp.read(CHUNK_SIZE)        
        try:
            resp = self._getView(urlBase,startKey=startKey,endKey=endKey,includeDocs=includeDocs)
            return streamResult(resp)
        except HTTPError as ex:
            abort(404, "not found")

    def _orderParmaByView(self,params,view):
        startKey=[]
        endKey=[] 
        def populateTs():
            if 'from' in params:
                startKey.append(self._convertDateTime(params['from']))
            else:
                startKey.append(self._convertDateTime(datetime.min.isoformat() + "Z"))
            if 'until' in params:
                endKey.append(self._convertDateTime(params['until']))
            else:
                endKey.append(self._convertDateTime(datetime.utcnow().isoformat()+"Z"))                
        def populateDiscriminator():
            if 'discriminator' in params:
                discriminator = params['discriminator']
                startKey.append(discriminator)
                endKey.append(discriminator+u'\ud7af')
            else:
                startKey.append('')
                endKey.append(u'\ud7af')
        def populateResource():
            if 'resource' in params:
                startKey.append(params['resource'])
                endKey.append(params['resource']+u'\ud7af')
            else:
                startKey.append('')
                endKey.append(u'\ud7af')       
        includeDocs = True
        if "ids_only" in params:
            includeDocs = not params
        funcs = {
            "discriminator":populateDiscriminator,
            'resource':populateResource,
            'ts':populateTs
        }       
        queryOrderParts = view.split('-by-')
        aggregate = queryOrderParts[0]
        queryParams= queryOrderParts[1].split('-')       
        for q in queryParams:
            funcs[q]()
        funcs[aggregate]()
        return startKey if len(startKey) > 0 else None, endKey if len(endKey) > 0 else None, includeDocs

    def get(self, dataservice="",view='',list=''):
        """GET /extract/id: Show a specific intem"""        
        try:
            db_url = '/'.join([appConfig['couchdb.url'],appConfig['couchdb.db.resourcedata']])        
            db = couchdb.Database(db_url)
            dsDocument = db['_design/'+dataservice]
            if "dataservices" not in dsDocument:
                abort(406, "Invalid Data Service")
                log.error("no dataservices element in document")
            urlBase = "_design/{0}/_list/{1}/{2}".format(dataservice,list,view)        
            startKey, endKey,includeDocs = self._orderParmaByView(request.params,view)
            return self._processRequest(startKey,endKey,urlBase,includeDocs)
        except couchdb.ResourceNotFound as ex:
            abort(406,"Invalid Data Service")
            log.error(ex)