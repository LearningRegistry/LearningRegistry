#!/usr/bin/python
import couchdb
publish_urls = ['http://lrdev1.learningregistry.org/resource_data','http://lrdev2.learningregistry.org/resource_data','http://lrdev3.learningregistry.org/resource_data']

for url in publish_urls:
    db = couchdb.Database(url)
    for id in db:
        data = db[id]
        if data.has_key('node_timestamp'):
            data['update_timestamp'] = data['node_timestamp']
            data['created_timestamp'] = data['node_timestamp']
            db[id] = data 
