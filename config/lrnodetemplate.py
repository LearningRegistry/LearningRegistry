import time

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
                    'services':[{
                                 "doc_type": "service_description",
                                 "doc_version": "0.10.0",
                                 "doc_scope": "node",
                                 "active": True,
                                 "service_id": "C47ADC73-987B-4EFE-BE32-77B241025795",
                                 "service_type": "access",
                                 "service_name": "OAI-PMH Harvest",
                                 "service_version": "0.10.0",
                                 "service_endpoint": "<nodeUrl>/OAI-PMH",
                                 "service_auth": "xxxx",    # a value that is not public access to the service
                                 "service_data": {
                                                  "version": "OAI-PMH 2.0",
                                                  "schemalocation": "http://www.learningregistry.org/documents/downloads/OAI-PMH-LR.xsd"    # location of the Learning Registry Extended OAI-PMH
                                                                # XSD used to validate service responses
                                                }
                                 },
                                {'active':        True,  
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
default_filter_description = {
                "doc_type": "filter_description",
                "doc_scope": "node",
                "active": True,
                "filter_name": "filter",
                "custom_filter": False,
                "include_exclude": True,
                "filter": [
                            {"filtering_keys": "test"},
                            {"doc_version": "0.10.0"}
                        ]}   
