_DOC_VERSION = "0.10.0"

community_description = {
                        "doc_type":"community_description",
                        "doc_version": _DOC_VERSION,
                        "doc_scope":"community",
                        "active": True,
                        "community_id":"COMMUNITY_X",
                        "community_name":"NAME_COMMUNITY_X",
                        "community_description":"Description of community X",
                        "community_admin_url":"optionalURL",
                        "social_community":True
                }
                
network_description = {   
                    "doc_type": "network_description",
                    "doc_version":_DOC_VERSION,
                    "doc_scope":"network",
                    "active":True,
                    "network_id": "NETWORK_A",
                    "network_name": "Name_A",
                    "network_description": "Description of test network named A",
                    "network_admin_url": "optional",
                    "community_id": community_description["community_id"]
                }

network_policy_description = {
            "doc_type": "policy_description", 
            "doc_version": _DOC_VERSION,
            "doc_scope": "network",
            "active":  True,
            "network_id": network_description['network_id'],
            "policy_id": network_description['network_id']+"_policy",
            "policy_version": "0.1",
            "TTL": 100  
            }
                            
node_description = {
                    "doc_type" :  "node_description",
                    "doc_version" : _DOC_VERSION,
                    "doc_scope":  "node",
                    "active": True,
                    "node_id":  "LR_TEST_NODE_1",
                    "node_name":  "node_name",
                    "node_description": "description",
                    "node_admin_url" : "string",
                    "network_id": network_description['network_id'],
                    "community_id": community_description['community_id'],
                    "gateway_node": False,
                    "open_connect_source" : False,
                    "open_connect_dest": False,
                    "node_policy":
                        {"sync_frequency" :  1,
                          "delete_data_policy": "no"
                        }
                }
                
node_filter_description= {
                    "doc_type": "filter_description",
                    "doc_version":"0.10.0",
                    "doc_scope": "node",
                    "active": True,
                    "filter_name": "filter",
                    "custom_filter": False,
                    "include_exclude": False,
                    "filter": [
                                {"filter_key": "keys",
                                 "filter_value": "test"}
                            ]
                }

node_services=[ 
                {
                    "doc_type": "service_description",
                    "doc_version": _DOC_VERSION,
                    "doc_scope": "node", 
                    "active": True,
                    "service_id": "publish_"+node_description['node_id'],
                    "service_type": "publish",
                    "service_name": "Name of publish service",
                    "service_description": "Publish service description", 
                    "service_version": "0.1", 
                    "service_endpoint": "string", 
                    "service_auth": "public",
                    "service_data":{}
                },
                 {
                    "doc_type": "service_description",
                    "doc_version": _DOC_VERSION,
                    "doc_scope": "node", 
                    "active": True,
                    "service_id": "access_"+node_description['node_id'],
                    "service_type": "access",
                    "service_name": "access service name",
                    "service_description": "access service description", 
                    "service_version": ".1", 
                    "service_endpoint": "string", 
                    "service_auth": "public",
                    "service_data":{}
                },
                 {
                    "doc_type": "service_description",
                    "doc_version": _DOC_VERSION,
                    "doc_scope": "node", 
                    "active": True,
                    "service_id": "broker_"+node_description['node_id'],
                    "service_type": "broker",
                    "service_name": "broker service name",
                    "service_description": "broker service description", 
                    "service_version": "0.1", 
                    "service_endpoint": "string", 
                    "service_auth": "public",
                    "service_data":{}
                },
                {
                    "doc_type": "service_description",
                    "doc_version": _DOC_VERSION,
                    "doc_scope": "node", 
                    "active": True,
                    "service_id": "administrative_"+node_description['node_id'],
                    "service_type": "administrative",
                    "service_name": "administrative service name",
                    "service_description": "broker service description", 
                    "service_version": "0.1", 
                    "service_endpoint": "string", 
                    "service_auth": "public",
                    "service_data":{}
                },
                 {
                    "doc_type": "service_description",
                    "doc_version": _DOC_VERSION,
                    "doc_scope": "node", 
                    "active": True,
                    "service_id": "distribute_"+node_description['node_id'],
                    "service_type": "distribute",
                    "service_name": "distribute service name",
                    "service_description": "distribute service description", 
                    "service_version": "0.1", 
                    "service_endpoint": "string", 
                    "service_auth": "public",
                    "service_data":{}
                }
            ]


node_connectivity= [
    {
           "doc_version": "0.10.0",
           "doc_type":"connection_description",
           "doc_scope": "node",
           "active": True,
           "connection_id": "API_Test_Node3_1",
           "source_node_url": "http://localhost/",
           "destination_node_url": "http://localhost/",
           "gateway_connection": False
    },
]
