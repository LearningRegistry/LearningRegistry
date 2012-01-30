#   Copyright 2011 Department of Defence

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging
import urllib2
import  couchdb
import  json
import re
import pprint
from pylons import request, response, session, tmpl_context as c, url, config
from pylons.controllers.util import abort, redirect
from lr.lib.base import BaseController, render
from  lr.model import ResourceDataModel, LRNode
from  lr.lib import ModelParser, SpecValidationException, helpers as  h
log = logging.getLogger(__name__)


class PublishController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('publish', 'publisher')
    __ERROR = 'error'
    __OK = "OK"
    __DOCUMENT_RESULTS =  'document_results'
    __DOCUMENTS = 'documents'
    
    def create(self):

        results = {self.__OK:True}
        error_message = None
        try:
            data = json.loads(request.body)
            doc_limit =  h.getServiceDocument(config['lr.publish.docid'])['service_data']['doc_limit']
            
            if len(data[self.__DOCUMENTS]) > doc_limit:
                error_message = "number of posted docs {0} exceeds doc limit: {1}".format(
                                               len(data['documents']), str(doc_limit))
                log.debug(error_message)
                results[self.__ERROR] = error_message
            else:
                results[self.__DOCUMENT_RESULTS ] = map(self._publish, data[self.__DOCUMENTS])
        except Exception as ex:
            log.exception(ex)
            results[self.__ERROR] = str(ex)
        
        if results.has_key(self.__ERROR):
           results[self.__OK] = False
        return json.dumps(results)
        
        
    def _isResourceDataFilteredOut(self, resourceData):
        
        if (LRNode.filterDescription is None or
            LRNode.filterDescription.filter is None or 
            LRNode.filterDescription.custom_filter == True):
            #Do custom the filter I supposed ... for now just resturn false.
            return [False, None]
        
        matchResult = False
        envelopFilter = ""
        for f in LRNode.filterDescription.filter:
            log.info("\n"+str(f)+"\n")
            # Ckeck if jsonObject object has the key if it has search 
            # for the regular expression in the filter otherwise keep looking
            key = f['filter_key']
            resourceValue = None
            
            for k in resourceData._specData.keys():
                if re.search(key, k) is not None:
                    resourceValue = str(resourceData.__getattr__(k))
                    break
                    
            if  resourceValue is None:
                continue
                
            value = f['filter_value']
            log.info("\n"+str(key)+", "+str(value)+", "+ resourceValue+"\n")
            if(re.search(value,  resourceValue) is not None):
                matchResult = True
                envelopFilter = "Filter '"+str(f)+"' for key '"+str(key)+\
                                          "' matches '"+resourceValue+"'"
                break
        
        #Check if what matching means base on the include_exclude
        # True: the filters describe what documents to accept all others
        # are rejected
        # False: the filters describe what documents to reject
        # all others are accepted
        if LRNode.filterDescription.include_exclude is None or \
            LRNode.filterDescription.include_exclude == True:
            if matchResult == False:
                return True, "\nDocument failed to match filter: \n"+\
                               pprint.pformat(LRNode.filterDescription.specData, indent=4)+"\n"
        else:
            if matchResult == True:
               return True, "\nExcluded by filter: \n"+envelopFilter
             
        return [False, None]
        
    def _publish(self, envelopData):
        if isinstance(envelopData,unicode):
            envelopeData = json.loads(envelopData)
            
        result={self.__OK: True}

        try:
            # Set the envelop data timestaps.
            timeStamp = h. nowToISO8601Zformat()
            for stamp in ResourceDataModel._TIME_STAMPS:
                    envelopData[stamp] = timeStamp
                    
            resourceData = ResourceDataModel(envelopData)
            #Check if the envelop get filtered out
            isFilteredOut, reason = self._isResourceDataFilteredOut(resourceData)
            if isFilteredOut:
                result[self.__ERROR] = reason
            else:
                resourceData.publishing_node = LRNode.nodeDescription.node_id
                resourceData.save()
                result[resourceData._DOC_ID] = resourceData.doc_ID 
                 
        except SpecValidationException as ex:
            log.exception(ex)
            result[self.__ERROR]  = "\n"+pprint.pformat(str(ex), indent=4)
        except Exception as ex:
            log.exception(ex)
            result[self.__ERROR]  = "internal error"
            
        if result.has_key(self.__ERROR):
            result[self.__OK] = False
        
        return result
