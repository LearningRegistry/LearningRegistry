#    Copyright 2011 SRI International
#    
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#    
#        http://www.apache.org/licenses/LICENSE-2.0
#    
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
'''
Simple script to delete all non-design docs out of couch.

Created on Feb 15, 2011

@author: jklo
'''

uri="http://localhost:5984"
path="/lrdemo/_design/envelope/_view/docs"

from restkit.resource import Resource
import json

def main():
    res = Resource(uri)
    clientResponse = res.get(path=path, headers={"Content-Type":"application/json"})
    body = clientResponse.body_string()
    docs = json.loads(body)
  
    deletable = []
    for result in docs["rows"]:
        doc = result[u'value']
        if doc.has_key(u'_id') == True and doc.has_key(u'_rev') == True:
            deletable.append({ "_id": doc[u'_id'], "_rev": doc[u'_rev'], "_deleted": True })
     
        
    clientResponse = res.post("/lrdemo/_bulk_docs", payload=json.dumps({"all_or_nothing": True, "docs": deletable}), headers={"Content-Type":"application/json"})
    body = clientResponse.body_string()
    print(body)
    print ("done")
    
if __name__ == '__main__':
    main()