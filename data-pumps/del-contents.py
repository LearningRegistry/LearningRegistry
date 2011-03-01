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