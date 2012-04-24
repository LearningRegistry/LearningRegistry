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
import collections, sys
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
            epoch = parse_date("1970-01-01T00:00:00Z")        
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
        def makeEndKey(key):
            from copy import deepcopy
            newkey = deepcopy(key)
            #if complex key
            if isinstance(newkey, list):
                # get last element in key
                last = newkey[-1]
                # if the last element is a list, just append an empty object to the last element's list
                if isinstance(last, list):
                    last.append({})
                # if the last element in an object, it becomes a bit tricky
                # *** note that the key parameter MUST have been originally json parsed with the object_pairs_hook=collections.OrderedDict otherwise
                #     key order won't be guaranteed to be the same as what CouchDB will use!!!!
                elif isinstance(last, dict):
                    lastkey = last.keys()[-1]
                    # since there's no easy way to increment a float accurately, instead append a new key that 'should' sort after the previous key.
                    if (isinstance(last[lastkey], float)):
                        last[lastkey+u'\ud7af'] = None
                    # if it's something else... this thing should recurse and keep going.
                    else:
                        last[lastkey] = makeEndKey(last[lastkey])
                # if we got here, it's nothing really special, so we'll just append a {} to newkey
                else:
                    newkey.append({})
            # this if to handle the odd case where we have string as either the key or the value of an object in a complex key.
            elif isinstance(newkey, (str, unicode, basestring)):
                newkey=newkey+u'\ud7af'
            # integer... so just increment 1.
            elif isinstance(newkey, int):
                newkey += 1
            
            # if we skipped everything else - we don't have a strategy to deal with it... so don't

            return newkey

        def makeStartsWithEndKey(key):
            from copy import deepcopy
            newkey = deepcopy(key)
            # this the base case for keys that are just strings, append the funky unicode char so that it grabs everything from
            # "foo" to "foo\ud7af", which is technically the only way we know how to deal with starts with.
            if isinstance(newkey, (str, unicode, basestring)):
                newkey=newkey+u'\ud7af'
            # if this is a complex key, then get the last element and recurse
            elif isinstance(newkey, list):
                newkey[-1] = makeStartsWithEndKey(newkey[-1])
            # if the last element in an object, it becomes a bit tricky, because you must modify the last key, which implies
            # order of keys was maintained when the value was originally parsed.
            # *** IMPORTANT: The key parameter MUST have been originally json parsed with the object_pairs_hook=collections.OrderedDict otherwise
            # ***            key order won't be guaranteed to be the same as what CouchDB will use!!!! 
            elif isinstance(last, dict):
                lastkey = last.keys()[-1]
                #take the value from the last key and recurse.
                last[lastkey] = makeEndKey(last[lastkey])
            # if we skipped everything else - we don't have a strategy to deal with it as a Starts With key, so just return 
            else:
                newkey = key

            return newkey

        def hasParamFor(funcName):
            if funcName == 'ts' and ('from' in params or 'until' in params):
                return True
            elif funcName == 'discriminator' and ('discriminator' in params or 'discriminator-starts-with' in params):
                return True
            elif funcName == 'resource' and ('resource' in params or 'resource-starts-with' in params):
                return True
            else:
                return False

        def populateTs(startKey, endKey, pos, isLast):
            if 'from' in params:
                startKey.append(self._convertDateTime(params['from']))
            elif pos == 1:
                startKey.append(self._convertDateTime(datetime.min.isoformat() + "Z"))

            if 'until' in params:
                endKey.append(self._convertDateTime(params['until']))
            elif pos == 1:
                endKey.append(self._convertDateTime(datetime.utcnow().isoformat()+"Z"))    

            return startKey, endKey   

        def populateDiscriminator(startKey, endKey, pos, isLast):
            if 'discriminator' in params:
                # preserve key order!!!
                try:
                    discriminator = json.loads(params['discriminator'], object_pairs_hook=collections.OrderedDict)
                except:
                    log.error(sys.exc_info()[0])
                    discriminator = params['discriminator']
                startKey.append(discriminator)
                endKey.append(discriminator)

            elif 'discriminator-starts-with' in params:
                # preserve key order!!!
                try:
                    discriminator = json.loads(params['discriminator-starts-with'], object_pairs_hook=collections.OrderedDict)
                except:
                    log.error(sys.exc_info()[0])
                    discriminator = params['discriminator-starts-with']
                startKey.append(discriminator)
                endKey.append(discriminator)
                endKey = makeStartsWithEndKey(endKey)
            return startKey, endKey
            # else:
            #     startKey.append('')
            #     endKey.append(u'\ud7af')
        def populateResource(startKey, endKey, pos, isLast):
            if 'resource' in params:
                startKey.append(params['resource'])
                endKey.append(params['resource'])
            elif 'resource-starts-with' in params:
                startKey.append(params['resource-starts-with'])
                endKey.append(params['resource-starts-with']+u'\ud7af')
            return startKey, endKey
            # else:
            #     startKey.append('')
            #     endKey.append(u'\ud7af') 
        startKey=[]
        endKey=[]      
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

        # if we don't have explicit params for this, then omit.
        if hasParamFor(aggregate):
            queryParams.append(aggregate)
            log.error("added aggregate")

        for pos, q in enumerate(queryParams,start=1):
            startkey, endKey = funcs[q](startKey, endKey, pos, len(queryParams)==pos)
        
        if len(endKey) > 0 and 'resource-starts-with' not in params and 'discriminator-starts-with' not in params:
            log.error("making endkey")
            endKey = makeEndKey(endKey)

        # startkey, endKey = funcs[aggregate](startKey, endKey, len(queryParams)+1, True)
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