#!/usr/bin/python
import couchdb, time
server = couchdb.Server()
def create(name):
    try:
        server.create(name)
    except:
        print 'DB already exists'
create('node')
create('resource_data')
create('community')
create('network')
db = server['node']
def publish_doc(name, doc_data):
    try:
        del db[name]
    except couchdb.http.ResourceNotFound as ex:
        print ex
    db[name] = doc_data
default_status = {'timestamp' :'',
                  'active':True, 
                  'node_id': '', 
                  'node_name':'',
                  'doc_count':'',
                  'install_time':time.asctime(),
                  'start_time':'',
                  'last_in_sync':'',
                  'in_sync_node':'',
                  'last_out_sync':'',
                  'out_sync_node':''  }
default_description = {'timestamp':        'string',
                       'active':        True,    
                       'node_id':        'string',
                       'node_name':        'string',
                       'node_description':    'string',
                       'node_admin_url':    'string',
                       'network_id':        'string',
                       'network_name':     'string',
                       'network_description':    'string',
                       'network_admin_url':    'string',
                       'community_id':    'string' ,
                       'community_name':     'string',
                       'community_description':'string',
                       'community_admin_url':'string',
                       'policy_id':        'string',
                       'policy_version':    'string',
                       'gateway_node':    True,
                       'open_connect_source':True,
                       'open_connect_dest':    True,
                       'social_community':    True,}
default_services = {'timestamp':        'string',
                    'active':        True,    
                    'node_id':        'string',
                    'node_name':        'string',
                    'services':[{'active':        True,  
                                 'service_id':        'string',
                                 'service_type':    'string',        
                                 'service_name':    'string',
                                 'service_description':    'string',
                                 'service_version':    'string',
                                 'service_endpoint':    'string',
                                 'service_auth':    'string',
                                 'service_data':    {}       
                              }]}
default_policy = {'timestamp':        'string',
                  'active':        True,
                  'node_id':        'string',
                  'node_name':        'string',
                  'network_id':        'string',
                  'network_name':     'string', 
                  'network_description':    'string',
                  'policy_id':        'string',    
                  'policy_version':    'string',
                  'TTL':            0}
publish_doc('status',default_status)
publish_doc('policy',default_policy)
publish_doc('description',default_description)
publish_doc('services',default_services)



