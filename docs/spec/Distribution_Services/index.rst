




============================================================================
Distribution Services: Learning Registry Technical Specification V DS:0.50.1
============================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.


:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.

This document is part of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It describes the Learning Registry services used to distribute resource documents throughout a distribution network.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General <../General_Matter/index>` :doc:`Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References

- :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>`

- :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Other <../Services_and_APIs/index>` :doc:`Services <../Services_and_APIs/index>` including :doc:`Publish <../Publish_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Broker <../Broker_Services/index>`, :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that specific criteria for services and APIs are presented in the :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part, the :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>` part describes the network model, the :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>` part describes the data that distribution services process, and the :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>` part describes security requirements.



.. _Resource Data Distribution Service:

----------------------------------
Resource Data Distribution Service
----------------------------------

The resource data distribution service is used to distribute (synchronize or replicate) the resource data from one node to its connected nodes (unidirectional).
The resource data distribution service SHALL :ref:`apply filters <Resource Data Filtering>`, if present at the destination node, to restrict the resource data that is distributed.
The resource data distribution service SHALL :ref:`apply validation <Resource Data Validation and Publication>` to restrict the resource data that is stored at the destination node.
A destination node MAY reject any resource data description document based on the node’s :ref:`policies <Resource Data ToS, Signatures and Trust Policy Enforcement>`: from an unverified or untrusted submitter, that is not signed or where the signature cannot be verified, that does not contain an accepted ToS, etc.
The destination node MAY reject any document that is larger than the node can store.
The destination node SHALL reject any document with a "do_not_distribute" key-value pair; this verification SHALL be performed before any other verification and SHALL short circuit all other verification.

*NB*: There is no defined mechanism to define the acceptable ToS for a node.

*NB*: How the resource data distribution service decides if it accepts or rejects resource data that does not come from a verified submitter, is not signed or that does not conform to the destination node’s ToS is determined by the the node’s policy and is not defined in this specification.

Future drafts or versions of this specification MAY define additional resource data distribution services.

The resource data distribution service is used in resource distribution network operations.
Access to the service SHOULD be restricted to network operational procedures.

The resource data distribution service examines the network topology and verifies the rules that govern network structure for each connection and the associated nodes.
On a connection-by-connection basis, a malformed connection between two nodes SHALL be skipped.
Distribution occurs across all valid connections.

*NB*: There is no assumption that one type of document (node description or connection) is more authoritative.

A task scheduler SHOULD trigger resource data distribution from a source node to all of its destination nodes according to the frequency specified by the sync_frequency in the node description document.


The service provides three distinct functions:

- A service with an API at the source node which is used to trigger the resource data distribution.
  

- A service at each destination node that processes the incoming resource data.

- A service and API at each destination node that is used to return descriptive information from the destination node to the source node to validate the connection.
  

API: Data Distribution
======================


.. http:post:: /distribute

    **Arguments:**

        None

    **Request Object:**

        None

    **Results Object:**                    // results summary and errors

    .. sourcecode:: javascript
    
        {

            "OK":        boolean,          // T if successful

            "error":        "string"       // text describing error

        }            

    :statuscode 200: no error
    :statuscode 500: error


Resource Distribution: Source Node Process
==========================================



    // Distribute a resource data description document collection from one node to its connected nodes

    VALIDATE resource_document_database.doc_type = "resource_data"

    // only distributing resource data

    GET the *network* *node* *description* document for the source node to obtain

        source.network_id

        source.community_id

        source.gateway_node

    GET the *network* *community* *description* document for the source node to obtain

        source.social_community

    GET the *network* *node* *connectivity* documents for the source node

        IF > 1 connectivity document with active = T AND gateway_connection = T

            THEN ABORT 

                                        // only one active gateway is allowed, faulty network description

        FOR EACH node connectivity document

            GET the *network* *node* *description* document for the destination node

                (via the destination_node_url) to obtain

                destination.network_id

                destination.community_id

                destination.gateway_node

            GET the *network* *community* *description* document for the destination node

                to obtain

                destination.social_community

            IF source.community_id <> destination.community_id

                AND ((NOT source,social_community) 

                    OR (NOT destination.social_community))

                    THEN SKIP

                                        // cannot distribute across non social communities

            IF (NOT gateway_connection) AND

                source.network_id <> destination.network_id

                    THEN SKIP

                                        // cannot distribute across networks (or communities) unless gateway

            IF gateway_connection AND

                source.network_id = destination.network_id

                    THEN SKIP

                                        // gateway must only distribute across different networks

            IF gateway_connection

                AND    ((NOT source.gateway_node)

                    (OR (NOT destination.gateway_node))

                    THEN SKIP

                                        // gateways can only distribute to gateways

            COMMIT all outstanding resource data description database operations

            PERFORM distribution service between source and destination nodes

                                        // this is the distribution primitive

*NB*: There may be a better way to do the validations via map-reduce.

*NB*: Since all attributes of the network that model its topology are immutable, the replication process should be transactionally safe.

*NB*: The process is only designed to distribute resource data.
It encodes specific business rules about gateway processing.
It SHOULD NOT be used to distribute network descriptions.

*NB*: The process does not return errors when there are bad connection descriptions; they are skipped.
A bad connection should never have been accepted; the checks are included to ensure consistency.

*NB*: The process does not return errors when a distribution fails, either directly or because the destination node is not available.
The process SHOULD verify that the destination node is reachable and operational before performing data distribution.

Resource Distribution: Destination Node Process
===============================================



        // Process and filter inbound resource data description documents at a node

        REJECT the *resource* *data* *description* document if it contains a do_not_distribute key.

        VALIDATE the *resource* *data* *description* document

                                        // skip storing all documents that do not validate

        REJECT the *resource* *data* *description* document if the submitter cannot be verified

        REJECT the *resource* *data* *description* document if the submitter_TOS is unacceptable to the node

        REJECT the *resource* *data* *description* document if it too large

        IF the *network* *node* *filter* *description* document exists and contains active filters

            THEN PERFORM filtering and store only documents that pass the filter

        `▲ UPDATE node_timestamp // when the document was stored at the node`:changes:



*NB*: The process does not return indicators when documents are filtered.

`▲ *NB*: An implementation SHALL maintain node_timestamp in a manner that does not trigger redistibution of the document; node_timestamp is a local node value`.:changes:
`-- TO BE replaced by a local value that is not maintained as part of the resource data description document`:deletions:

API: Destination Node Information
=================================


.. http:get:: /destination

    **Arguments:**

        None

    **Request Object:**

        None

    **Results Object:**                    

    .. sourcecode:: javascript
    
        {                                   // results summary and errors

            "OK":        boolean,           // T if successful

            "error":        "string",       // text describing error

            "target_node_info":             // target distribution node data

            {

                "active":        boolean,       // is the destination network node active

                "node_id":        "string",     // ID of the destination network node

                "network_id":        "string",  // id of the network of the destination

                "community_id":    "string",    // id of the community of the destination

                "gateway_node":    boolean,     // destination node is a gateway node

                "social_community":    boolean  // is community a social community

            }

        }



    :statuscode 200: no error
    :statuscode 500: error 


Resource Distribution: Destination Node Information
===================================================


    // Return the description of a destination network node

    DEFINE VIEW on

        *network* *node* *description* document containing the required output fields

        + *network* *community* *description* document containing the required output fields

    QUERY

    RETURN Results document

    

Service Description
===================

::

    {

        "doc_type": "service_description",

        "doc_version": "0.20.0",

        "doc_scope": "node",

        "active": true,

        "service_id": "<uniqueid>",

        "service_type": "distribute",

        "service_name": "Resource Data Distribution",

        "service_description": "Service used to distribute resource documents from one node to other nodes",

        "service_version": "0.23.0",

        "service_endpoint": "<node-service-endpoint-URL>",

        "service_auth": 
                                                // service authentication and authorization descriptions
        {

            "service_authz": ["<authvalue>"],
                                                // authz values for the service

            "service_key": < T / F > ,
                                                // does service use an access key   

            "service_https": < T / F > // does service require https
        }

    }

The service definition is only for the source node.
There is no service definition for the target node API used to get the target node information.

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.





----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                       |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document.Archived copy (V 0.24.0)                                                                                                           |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V DS:0.49.0)                                                                                                        |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | TBD      | DR         | Renumber all document models and service documents. Added node policy to control storage of attachments (default is stored). Archived copy location TBD. (V DS:0.50.0)                           |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Deprecate node_timestamp. Details of attachments on publish, obtain, harvest.Archived copy location TBD. (V DS:x.xx.x)                                                                           |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | This document extracted from Google Doc and converted to RestructuredText. `Archived copy (V DS:0.49.0) <https://docs.google.com/document/d/1HW_JJBiWxNHoA5L1TuZrjWeK-DaFF0FTeMZBNIL5MqI/edit>`_ |
|             |          |            | node_timestamp removed from deprecation.                                                                                                                                                         |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+




----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
