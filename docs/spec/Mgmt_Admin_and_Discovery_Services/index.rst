


========================================================================================================
Management, Administrative and Discovery Services: Learning Registry Technical Specification V MS:0.50.1
========================================================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.

:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.


This document is part of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It describes the basic Learning Registry services used to manage, administer and perform discovery in a distribution network.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General <../General_Matter/index>` :doc:`Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References

- :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>`

- :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Other <../Services_and_APIs/index>` :doc:`Services <../Services_and_APIs/index>` including :doc:`Distribution <../Distribution_Services/index>`, :doc:`Publish <../Publish_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Broker <../Broker_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that specific criteria for services and APIs are presented in the :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part, the :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>` part describes the network model and the :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>` part describes security requirements.

.. _Administrative Services:

"""""""""""""""""""""""
Administrative Services
"""""""""""""""""""""""

Administrative services are used to trigger network node administrative operations, to determine node status or to retrieve descriptive information about a network node.
They are used to support monitoring and discovery.
Future drafts or versions of this specification MAY define additional administrative services.
Future drafts or versions of this specification MAY define additional service query arguments that will customize the returned data.

*NB*: Provisioning administrative services is optional.
They SHOULD NOT be relied on for resource distribution network operations.

*Open Question*: Do we need to have separate services to return node filters (now part of the general node description) or node connectivity (currently not retrievable).

All administrative services SHALL support HTTP content negotiation.
All administrative services SHALL support return of CONTENT-TYPE: text/plain.
All administrative services SHOULD support return of text/html, text/xml, application/rdf+xml.


.. _Network Node Status Service:

---------------------------
Network Node Status Service
---------------------------

The network node status service is used to return information and operational data about a network node.
The service SHALL return all of the key-value pairs listed that have a valid value.
The service MAY return additional key-value pairs that indicate status.

A network node SHALL maintain all of the data necessary to return the required key-value pairs.

API
===

.. http:get:: /status
   

        **Arguments:**

            None

        **Request Object:**    

            None

        **Results Object:**

        .. sourcecode:: http

            {
                "timestamp": "string",              
                                        // time of report, time/date encoding

                "active": boolean; 
                                        // is the network node active

                "node_id": "string", 
                                        // ID of the network node

                "node_name": "string", 
                                        // name of the network node

                "doc_count": integer, 
                                        // number of unique:changes:` `resource data documents

                                        // held by the node

                                        //  only count distributable documents

                "total_doc_count": integer, 
                                        // number of unique resource data documents

                                        // held by the node

                                        // including non distributable documents

                "install_time": "string", 
                                        // time/date of node install

                "start_time": "string", 
                                        // server restart time/date

                                        // last reboot 

                "last_in_sync": "string", 
                                        // time of last inbound sync

                                        // omit if node has not sync’ed

                "in_sync_node": "string", 
                                        // id of the node from the last inbound sync

                                        // omit if node has not sync’ed

                "last_out_sync": "string", 
                                        // time of last outbound sync

                                        // omit if node has not sync’ed

                "out_sync_node": "string", 
                                        // id of the node for the last outbound sync

                                        // omit if node has not sync’ed

                "earliestDatestamp": "string" 
                                        // oldest timestamp for harvest

                                        // time/date encoding

            }

Network Node Status
===================

    // Return the operational status of a network node

    DEFINE VIEW on 

                *network node description* document containing the required fields 

                + *network node operational* data containing the required fields

    QUERY

    TRANSFORM results to specified CONTENT-TYPE

Service Description
===================

::

    {   
        "doc_type": "service_description",

        "doc_version": "0.20.0",

        "doc_scope": "node",

        "active": true,

        "service_id": "<uniqueid>",

        "service_type": "access",

        "service_name": "Network Node Status",

        "service_description": "Service to retrieve basic operational status information for a node",

        "service_version": "0.23.0",

        "service_endpoint": "<node-service-endpoint-URL>",

        "service_auth": 
                                        // service authentication and authorization descriptions

        {

            "service_authz": ["<authvalue>"], 
                                        // authz values for the service

            "service_key": < T / F > , 
                                        // does service use an access key            

            "service_https": < T / F > 
                                        // does service require https

        }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.


.. _Network Node Description Service:

--------------------------------
Network Node Description Service
--------------------------------

The network node description service is used to return descriptive information about a network node, the resource distribution network that it is a part of and the network community that it is a part of.
The service SHALL return all of the key-value pairs listed that have a valid value.
An implementation MAY omit the return of any key-value pair that is an optional key-value pair in a :ref:`Network Data Model <Network Data Models>` for which a value is missing or NULL.
The service MAY return additional informational values.

API
===


.. http:get:: /description
   

        **Arguments:**

            None

        **Request Object:**    

            None

        **Results Object:**
        
        .. sourcecode:: http

            {
                "timestamp": "string",        
                                        // time of report, time/date encoding

                "active": boolean;    
                                        // is the network node active

                "node_id": "string",        
                                        // ID of the network node

                "node_name": "string",        
                                        // name of the network node

                "node_description": "string",        
                                        // description of the node

                "node_admin_identity": "string",        
                                        // identity of node admin

                "node_key": "string",        
                                        // node public key

                "network_id": "string",        
                                        // id of the network

                "network_name": "string",        
                                        // name of the network

                "network_description": "string",        
                                        // description of the network

                "network_admin_identity": "string",        
                                        // identity of network admin

                "network_key": "string",    
                                        // network public key

                "community_id": "string",    
                                        // id of the community

                "community_name": "string",        
                                        // name of the community

                "community_description: "string",        
                                        // description of the community

                "community_admin_identity": "string",        
                                        // identity of community admin

                "community_key": "string",        
                                        // community public key

                "policy_id": "string",        
                                        // id of the policy description

                "policy_version": "string",        
                                        // version identifier for the policy

                "gateway_node": boolean,    
                                        // node is a gateway node            

                "open_connect_source": boolean,    
                                        // node is willing to be a source

                "open_connect_dest": boolean,    
                                        // node is willing to be a destination

                "social_community": boolean,    
                                        // is community is a social community

                "node_policy":                
                                        // node-specific policies, optional

                {   
                    "sync_frequency": integer,        
                                        // target time between synchronizations

                    "deleted_data_policy": "string",        
                                        // policy value

                    "TTL": integer,        
                                        // minimum time to live for resource data 

                    "accepted_version": ["string"],    
                                        // list of resource data description document 

                                        // versions that the node can process

                    "accepted_TOS": ["string"],    
                                        // list of ToS that the node will accept    

                    "accepts_anon": boolean,    
                                        // node takes anonymous submissions

                    "accepts_unsigned": boolean,    
                                        // node takes unsigned submissions

                    "validates_signature": boolean,    
                                        // node will validate signatures

                    "check_trust": boolean,    
                                        // node will evaluate trust of submitter

                    "max_doc_size": integer        
                                        // max document size that a node stores

                }

                "filter":                    
                                        // filter data
                
                {   
                    "filter_name": "string",         
                                        // name of the filter

                    "custom": boolean,    
                                        // custom filter

                    "include_exclude": boolean,    
                                        // accept or reject list

                    "filters":[                
                                        // array of filter rules

                    {
                        "filter_key": "string",        
                                        // REGEX that matches names

                        "filter_value": "string"        
                                        // REGEX that matches values

                    }]

                }

            }

Network Node Description
========================

    // Return the description of a network node

    DEFINE VIEW on 

                *network node description* document containing the required output fields 

                + *resource distribution network description* document containing the required output fields

                + *resource distribution network policy* document containing the required output fields

                + *network community description* document containing the required output fields

                + *network node filter description* document containing the required output fields

    QUERY

    TRANSFORM results to specified CONTENT-TYPE

Service Description
===================

::

    {

        "doc_type": "service_description",

        "doc_version": "0.20.0",

        "doc_scope": "node",

        "active": true,

        "service_id": "<uniqueid>",

        "service_type": "access",

        "service_name": "Network Node Description",

        "service_description": "Service to retrieve a comprehensive description of a node",

        "service_version": "0.23.0",

        "service_endpoint": "<node-service-endpoint-URL>",

        "service_auth": 
                                        // service authentication and authorization descriptions

            {"service_authz": ["<authvalue>"], 
                                        // authz values for the service

            "service_key": < T / F > , 
                                        // does service use an access key            

            "service_https": < T / F > 
                                        // does service require https
    
            }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.


.. _Network Node Services Service:

-----------------------------
Network Node Services Service
-----------------------------

The network node services service is used to return the list of services available at a network node.
For each service at a node, the service SHALL return all of the key-value pairs listed that have a valid value.
An implementation MAY omit the return of any key-value pair that is an optional key-value pair in a :ref:`Network Data Model <Network Data Models>` for which a value is missing or NULL.
The service MAY return additional key-value pairs for a service.


The service SHOULD group and sort the results in some logical form, e.g., by ACTIVE, by TYPE.

API
===


.. http:post:: /services    

        **Arguments:**

            None

        **Request Object:**    

            None

        **Results Object:**

        .. sourcecode:: http
        
            {
                "timestamp": "string",        
                                        // time of report, time/date encoding

                "active": boolean;    
                                        // is the network node active

                "node_id": "string",        
                                        // ID of the network node

                "node_name": "string",        
                                        // name of the network node

                "services":[                
                                        // array of service description objects

                {   
                    "active": boolean;    
                                        // is the service active

                    "service_id": "string",        
                                        // id of the service

                    "service_type": "string",        
                                        // fixed vocabulary

                    "service_name": "string",        
                                        // name of the service

                    "service_description": "string",        
                                        // description of the service

                    "service_version": "string",        
                                        // version number of the service description

                    "service_endpoint": "string",        
                                        // URL of service

                    "service_auth":            
                                        // service authentication and authorization descriptions

                    {
                        "service_authz": ["string"],     
                                        // authz values for the service

                        "service_key": boolean,    
                                        // does service use an access key                  
        
                        "service_https": boolean        
                                        // does service require https

                    },

                    "service_data": {}        
                                        // service-specific name-value pairs

                }]

            }

Network Node Services
=====================

    // Return the description of network node services

    DEFINE VIEW on 

                *network node description* document containing the required output fields 

                + ALL *network node service description* documents containing the required output fields

                GROUPED and ORDERED on service attributes.

    QUERY

    TRANSFORM results to specified CONTENT-TYPE

Service Description
===================

::

    {
        "doc_type": "service_description",

        "doc_version": "0.20.0",

        "doc_scope": "node",

        "active": true,

        "service_id": "<uniqueid>",

        "service_type": "access",

        "service_name": "Network Node Services",

        "service_description": "Service to retrieve the list of services deployed at a node",

        "service_version": "0.21.0",

        "service_endpoint": "<node-service-endpoint-URL>",

        "service_auth": 
                                        // service authentication and authorization descriptions

            {
            
            "service_authz": ["<authvalue>"],
                                        // authz values for the service

            "service_key": < T / F > , 
                                        // does service use an access key            

            "service_https": < T / F > 
                                        // does service require https

            }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.


.. _Resource Distribution Network Policy Service:

--------------------------------------------
Resource Distribution Network Policy Service
--------------------------------------------

The resource distribution network policies service is used to return information about the policies that apply to the resource distribution network that the network node is a part of.
The service SHALL return all of the key-value pairs listed that have a valid value.
An implementation MAY omit the return of any key-value pair that is an optional key-value pair in a :ref:`Network Data Model <Network Data Models>` for which a value is missing or NULL.
The service MAY return additional policy key-value pairs.
The service MAY be called at any node in the resource distribution network; all network nodes store an identical copy of the policy data.

API
===

.. http:get:: /policy

        **Arguments:**

            None

        **Request Object:**    

            None

        **Results Object:**

        .. sourcecode:: http
                
            {

                "timestamp": "string", 
                                        // time of report, time/date encoding

                "active": boolean; 
                                        // is the network node active

                "node_id": "string", 
                                        // ID of the network node

                "node_name": "string", 
                                        // name of the network node

                "network_id": "string", 
                                        // id of the network

                "network_name": "string", 
                                        // name of the network

                "network_description": "string", 
                                        // description of the network

                "policy_id": "string", 
                                        // id of the policy description

                "policy_version": "string", 
                                        // version identifier for the policy

                "TTL": integer 
                                        // minimum time to live for resource data

            }

Resource Distribution Network Policy
====================================

    // Return the description of network policies

    DEFINE VIEW on 

                *network node description* document containing the required output fields 

                + *resource distribution network description* document containing the required output fields

                + *resource distribution network policy* document containing the required output fields

    QUERY

    TRANSFORM results to specified CONTENT-TYPE

Service Description
===================

::

    {

        "doc_type": "service_description",

        "doc_version": "0.20.0",

        "doc_scope": "node",

        "active": true,

        "service_id": "<uniqueid>",

        "service_type": "access",

        "service_name": "Resource Distribution Network Policy",

        "service_description": "Service to retrieve network policies from a node",

        "service_version": "0.21.0",

        "service_endpoint": "<node-service-endpoint-URL>",

        "service_auth": 
                                        // service authentication and authorization descriptions

            {

            "service_authz": ["<authvalue>"], 
                                        // authz values for the service

            "service_key": < T / F > , 
                                        // does service use an access key            

            "service_https": < T / F > 
                                        // does service require https

            }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.



----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                 |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document. `Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_                 |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V MS:0.49.0)                                                                                                                  |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | TBD      | DR         | Renumber all document models and service documents. Added node policy to control storage of attachments (default is stored). Archived copy location TBD. (V MS:0.50.0)                                     |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Archived copy location TBD. (V MS:x.xx.x)                                                                                                                                                                  |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | This document extracted from original Google Doc and converted to RestructuredText. `Archived copy (V MS:0.49.0) <https://docs.google.com/document/d/1lATgircOBUOmsoFwia8su2o--TZ88AG4GOmn5NQ6jAc/edit>`_  |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
