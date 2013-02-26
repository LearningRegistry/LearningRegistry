

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.u6sbhsuktqyj:

Publish Services: **Learning** **Registry** **Technical** **Specification** **V** **PS****:0.**49**.0**
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Draft in Progress.
See the :ref:`Change<h.e1519o-y653zc>` :ref:`Log<h.e1519o-y653zc>` for links to prior stable versions.


:changes:`Shading`:changes:` `:changes:`indicates`:changes:` `:changes:`major`:changes:` `:changes:`changes`:changes:` `:changes:`and`:changes:` `:changes:`additions`:changes:` `:changes:`from`:changes:` `:changes:`the`:changes:` `:changes:`prior`:changes:` `:changes:`version`:changes:` (0.24.0).
`:changes:`Also`:changes:` `:changes:`indicated`:changes:` `:changes:`with` ▲:changes:`.`

:deletions:`Significant`:deletions:` `:deletions:`deletions`:deletions:` `:deletions:`are`:deletions:` `:deletions:`shaded`:deletions:`.`

:deprecation:`Features`:deprecation:` `:deprecation:`to`:deprecation:` `:deprecation:`be`:deprecation:` `:deprecation:`deprecated`:deprecation:` `:deprecation:`in`:deprecation:` `:deprecation:`a`:deprecation:` `:deprecation:`future`:deprecation:` `:deprecation:`version`:deprecation:` `:deprecation:`are`:deprecation:` `:deprecation:`shaded`:deprecation:` `:deprecation:`and`:deprecation:` `:deprecation:`indicated`:deprecation:` `:deprecation:`with`▼:deprecation:`.`

This document is part of one or more versions of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.

    :ref:`Publish<h.u6sbhsuktqyj>` :ref:`Services<h.u6sbhsuktqyj>`:ref:`: <h.u6sbhsuktqyj>`:ref:`Learning<h.u6sbhsuktqyj>` :ref:`Registry<h.u6sbhsuktqyj>` :ref:`Technical<h.u6sbhsuktqyj>` :ref:`Specification<h.u6sbhsuktqyj>` :ref:`V<h.u6sbhsuktqyj>` :ref:`PS<h.u6sbhsuktqyj>`:ref:`:0.49.0<h.u6sbhsuktqyj>`

        :ref:`Resource<h.xf8fiul5s5dl>` :ref:`Data<h.xf8fiul5s5dl>` :ref:`Publish<h.xf8fiul5s5dl>` :ref:`Services<h.xf8fiul5s5dl>`

                :ref:`Basic<h.aera9k-4u6l42>` :ref:`Publish<h.aera9k-4u6l42>` :ref:`Service<h.aera9k-4u6l42>`

                :ref:`SWORD<h.jl9f1nnwcev4>` :ref:`Publish<h.jl9f1nnwcev4>` :ref:`Service<h.jl9f1nnwcev4>`

                    :ref:`Retrieve<h.ku7eedtbq15d>` :ref:`Service<h.ku7eedtbq15d>` :ref:`Document<h.ku7eedtbq15d>`

                    :ref:`Create<h.2o7qqzkocz2j>` :ref:`a<h.2o7qqzkocz2j>` :ref:`Resource<h.2o7qqzkocz2j>`

                :ref:`Basic<h.rfe7ga-6sbjly>` :ref:`Delete<h.rfe7ga-6sbjly>` :ref:`Service<h.rfe7ga-6sbjly>`

        :ref:`Change<h.e1519o-y653zc>` :ref:`Log<h.e1519o-y653zc>`

        :ref:`Working<h.tph0s9vmrwxu>` :ref:`Notes<h.tph0s9vmrwxu>` :ref:`and<h.tph0s9vmrwxu>` :ref:`Placeholder<h.tph0s9vmrwxu>` :ref:`Text<h.tph0s9vmrwxu>`

This document is part of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It describes the basic Learning Registry services used to publish (push) resource documents into a distribution network.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General <../General_Matter/index>` :doc:`Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References

- :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>`

- :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Other <../Services_and_APIs/index>` :doc:`Services <../Services_and_APIs/index>` including :doc:`Distribution <../Distribution_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Broker <../Broker_Services/index>`, :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that specific criteria for services and APIs are presented in the :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part, the :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>` part describes the network model, the :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>` part describes the model of published data and the :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>` part describes security requirements.


""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.xf8fiul5s5dl:

Resource Data Publish Services
""""""""""""""""""""""""""""""""""""""""""""""""""""

Publish services are used to push resource data into the network.
They are used by external publishing edge nodes.
All resource data publishing services SHALL `apply <https://docs.google.com/a/learningregistry.org/document/d/1p-6XFb_eBlVYiGb9fZYtcQ4Z363rjysgS2PiZLXzAyY/edit?hl=en_US#heading=h.tph0s9vmrwxu>`_ `filters <https://docs.google.com/a/learningregistry.org/document/d/1p-6XFb_eBlVYiGb9fZYtcQ4Z363rjysgS2PiZLXzAyY/edit?hl=en_US#heading=h.tph0s9vmrwxu>`_ if present to restrict the resource data that is published to the node.
All resource data publishing services SHALL `apply <https://docs.google.com/a/learningregistry.org/document/d/1p-6XFb_eBlVYiGb9fZYtcQ4Z363rjysgS2PiZLXzAyY/edit?hl=en_US#heading=h.rw8jrb-9tha8>`_ `validation <https://docs.google.com/a/learningregistry.org/document/d/1p-6XFb_eBlVYiGb9fZYtcQ4Z363rjysgS2PiZLXzAyY/edit?hl=en_US#heading=h.rw8jrb-9tha8>`_ to restrict the resource data that is published to the node.
The validation process MAY also provide local updates to the resource document prior to it being published.
Any resource data publishing service MAY reject any resource data for any reason:

- From an untrusted submitter

- From an anonymous submitter

- Not signed

- Signature not valid

- Does not conform to the node’s ToS.

- Is larger than the node can store.
  

All resource data publishing services SHALL reject any document with a "do_not_distribute" key-value pair; this verification SHALL be performed before any other verification and SHALL short circuit all other verification.

*NB*: There is no defined mechanism to define the acceptable ToS for a node.
A node MAY advertise acceptable ToS in the node description document, but this MAY not be accurate.

*NB*: How a data publishing service decides if it accepts or rejects resource data that comes from an untrusted submitter, is not signed, signature cannot be validated, or that does not conform to the data publishing service’s ToS is determined by the data publishing service’s policy and is not defined in this specification.

*NB*: How a data publishing service decides that a document is too large is determined by the data publishing service’s policy and is not defined in this specification.

Future drafts or versions of this specification MAY define additional resource data publish services.


""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.aera9k-4u6l42:

**Basic** **Publish** **Service**
""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The basic publish service pushes an instance of a resource data description document (or a set of documents) directly to a node in a resource distribution network.
It is the most basic, direct mechanism to publish resource data.


Each resource data description document in the supplied set is published independently.
In addition to the overall service return indicating status, there SHALL be one returned object per resource data description document, aligned 1:1 to the documents in the supplied resource data description document array, indicating status of publishing of the resource data description document.

Each resource data description document SHALL be published to the node’s resource data description document database.
Prior to being published, it SHALL be validated: e.g., the syntax MUST be correct, mandatory values MUST be present, all values MUST come from the appropriate data space.
The document SHALL also be subject to all filters defined at the node.
Documents that do not pass the filters SHALL NOT be published.
The document MAY also be subject to verification of ToS and submitter information (including presence and validity of digital signature).
Documents from anonymous submitters, untrusted submitters, unsigned documents, or documents with a ToS that is not acceptable to the node MAY be rejected.
Documents that are too large MAY be rejected.

The publication process provides values for specific elements in the resource data description document.

If the resource data description document does not have an assigned identifier, the service SHALL assign one and return the value.


If the resource data description document has an identifier and a document with the same identifier exists in the resource data description document collection, the new document SHALL be an update, replacing the existing document in total.
If the resource data description document is being updated, the value of an immutable element SHALL NOT be changed.

The publication process SHALL set values for publish_node, , update_timestamp, ▼:deprecation:`node`:deprecation:`_`:deprecation:`timestamp`, node_timestamp, create_timestamp.
All timestamp values SHALL be the identical.
All timestamp values SHALL be UTC 0.

*NB*: There are no restrictions on the size of a batch publish document set, either in the number of elements or the total size of the HTTP message.
An implementation SHALL indicate any size limits in the service description.

*NB*: The process currently does not handle attachments.

*NB*: The process currently does not support updating published documents.

*Open* *Question*: Publishing to the node is by the node owner.
Do we need more to support trust?

*NB*: The process currently does not handle attachments.

**API**

        POST <node-service-endpoint-URL>/publish

    

        Arguments:

            None

        Request Object:                    // resource data to be published

            {"documents": 

                 [                    // array of

             {resource_data_description}        // resource data description documents

            ]}

        Results Object:

        {

         "OK":        boolean,        // T if successful

         "error":        "string",            // text describing global error

                            // present only if NOT OK

        "document_results":

        [                    // array of per document results

         {

         "doc_ID":    "string",            // ID of the document

         "OK":        boolean            // T if document was published

         "error":        "string"            // text describing error or filter failure

                            // present only if NOT OK

         }

         ]

        }

        Return Codes:

            200

            500

**Basic** **Publish**

    // Publish each resource data description document in the supplied list

        // Perform Validation    

         VALIDATE the *resource* *data* *description* document does not contain a do_not_distribute key.

        IF do_not_distribute key is present

            THEN     // create the global error object

                                OK := F

                error := "cannot publish" // an appropriate error for global condition

:changes:`            `    EXIT

    VALIDATE the publish request // apply appropriate business rules

        IF there is an overall error 

            THEN     // create the global error object

                                OK := F

                error := "error msg" // an appropriate error for global condition

                EXIT

    OK := T // global return status

    FOR EACH *resource* *data* *description* document

        VALIDATE the *resource* *data* *description* document // all syntactical and semantic rules

        IF there is an error

            THEN // create an error object array element object for the individual document    

                                OK := F

                error := "error msg" // an appropriate error for the document

                doc_ID := supplied doc_ID 

                                SKIP

                IF the *network* *node* *filter* *description* document exists and contains active filters

                        THEN PERFORM filtering and store only documents that pass the filter

                        IF the *resource* *data* *description* document does NOT pass the filter

                            THEN // indicate filtering was applied

                                        OK := F

                    error := "rejected by filter" // an appropriate filtering message

                    doc_ID := supplied doc_ID 

                                        SKIP

        IF the service applies ToS checks

                        AND the *resource* *data* *description* document TOS is unacceptable

                    THEN // indicate ToS was rejected

                                        OK := F

                    error := "rejected by ToS" // an appropriate message

                    doc_ID := supplied doc_ID 

                                        SKIP

        IF the service does not accept anonymous submissions

                        AND the *resource* *data* *description* document has submitted_type=="anonymous"

                    THEN // indicate submitted type was rejected

                                        OK := F

                    error := "anon submission rejected" // an appropriate message

                    doc_ID := supplied doc_ID 

                                        SKIP

            IF the service validates the submitter

                        AND the *resource* *data* *description* document submitter cannot be verified or trusted

                                THEN // indicate submitter was rejected

                                        OK := F

                    error := "rejected submitter" // an appropriate message

                    doc_ID := supplied doc_ID 

                                        SKIP

                IF the service requires a signature

                        AND the *resource* *data* *description* document signature not present

                                THEN // indicate signature was rejected

                                        OK := F

                    error := "no signature" // an appropriate message

                    doc_ID := supplied doc_ID 

                                        SKIP

                 IF the service validates the signature

                        AND the *resource* *data* *description* document signature cannot be verified

                                THEN // indicate signature was rejected

                                        OK := F

                    error := "rejected signature" // an appropriate message

                    doc_ID := supplied doc_ID 

                                        SKIP

                IF the node limits the size of document that can be stored

                        AND the *resource* *data* *description* document is too large

                                THEN // indicate document too large

                                        OK := F

                    error := "too large" // an appropriate message

                                        doc_ID := supplied doc_ID

                                        SKIP

                IF *resource* *data* *description* document did not have a supplied doc_ID

            THEN generate a new unique doc_ID

        PUBLISH the *resource* *data* *description* document to the node

                        by the owner of the node 

                     to the node’s resource data description document database

                    SET publish_node, update_timestamp,▼:deprecation:`node`:deprecation:`_`:deprecation:`timestamp`, create_timestamp

        IF there is a publishing error

            THEN // create an error object array element object for the individual document    

                                OK := F

                error := "publish failed" // an appropriate error for the publish failure

                doc_ID := supplied doc_ID 

                                SKIP

        // create a return object array element object for the individual document

        OK := T

        doc_ID // supplied or generated doc_ID

    

**Service** **Description**

    {

         "doc_type":        "service_description",    

         "doc_version":        "0.20.0",

         "doc_scope":        "node",

         "active":        true,

         "service_id":        "<uniqueid>",        

         "service_type":        "publish",

     "service_name":    "Basic Publish",    

        "service_description":"Service to directly publish one or more resource description documents to the node",    

     "service_version":    "0.23.0",

     "service_endpoint":    "<node-service-endpoint-URL>",

     "service_auth":                // service authentication and authorization descriptions

     {

     "service_authz":    ["<authvalue>"],     // authz values for the service

     "service_key":        <T/F>,        // does service use an access key            

     "service_https":    <T/F>        // does service require https

     },

      "service_data": 

         {

     "doc_limit":        integer,         // specify the maximum number of documents in a batch

     "msg_size_limit":    integer         // specify the maximum message size

     }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
Appropriate values for the service_data elements SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.


"""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.jl9f1nnwcev4:

**SWORD** **Publish** **Service**
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

`SWORD <http://www.google.com/url?q=http%3A%2F%2Fswordapp.org%2F&sa=D&sntz=1&usg=AFQjCNHNjbuSIPXGlVbbWTlOZJYcQXnMSQ>`_ (Simple Web-service Offering Repository Deposit) is a profile of the Atom Publishing Protocol (known as APP or ATOMPUB).
The SWORD APP API provides a mechanism for a repository to publish its metadata or paradata to a node in the resource distribution network.
Unless specified, the service SHALL support the SWORD V 1.3 protocol.

The SWORD service currently supports publishing of a resource data description document to a node.
A node corresponds to a SWORD collection; there is only one collection to deposit to.
The service supports SWORD developer features and mediated deposit.
The service currently only supports the deposit JSON encoded resource data description documents.
Package support is currently not specified.

The service end points for the protocol operations are:

+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| **Atom** **Pub** **Protocol** **Operation** | **SWORD** **API** **Endpoint**                                                                                                  |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Retrieving a Service Document               | GET <node\-service\-endpoint\-url>/swordservice                                                                                 |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Listing Collections                         | Currently not supported. To be added in a later version of the specification.                                                   |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Creating a Resource                         | POST <node\-service\-endpoint\-url>/swordpub                                                                                    |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Editing a Resource                          | Currently not supported. May be added in a later version of the specification.                                                  |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Deleting a Resource                         | Currently not supported. May be added in a later version of the specification                                                   |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+
| Retrieving a Resource                       | Not supported \-\- provided via the :ref:`Atom<h.1qn5t6\-ubytij>` :ref:`Pub<h.1qn5t6\-ubytij>` :ref:`Service<h.1qn5t6\-ubytij>` |
+---------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------+

*Open* *Question*: Should SWORD just publish the raw metadata or paradata document and let the service create the JSON?

Each of the protocol operations are specified separately.
The Service Description document SHALL apply to the entire API.


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.ku7eedtbq15d:

**Retrieve** **Service** **Document**
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The SWORD Service Document endpoint SHALL return an XML SWORD Service Document with the following settings:

- Global element settings:

- <sword:version> element: 1.3

- <sword:verbose> element: true

- <sword:noOp> element: true

- Workspace settings: There SHALL be only one workspace.
  The <title> element of the workspace SHALL be the community_name from the *network* *community* *description* *data* *model*.
  If the community_name is missing, the value SHALL be the community_id from the *network* *community* *description* *data* *model**.*

- Collection settings: There SHALL be only one collection.

  - IRI (http attribute): URL of the network node

  - <title> element: The title of the collection SHALL be the node_name from the *network* *node* *description* *data* *model*.
    If the node_name is missing, the value SHALL be the node_id from the *network* *node* *description* *data* *model*.

  - <accept> element: application/json

  - <sword:mediation> element: true

  - <dcterms:abstract> element: The abstract SHALL be the node_description from the *network* *node* *description* *data* *model*.
    If the node_description is missing, the element SHALL be omitted.

  - <sword:collectionPolicy> element MAY be present.
    The value is determined by the policies of the node, network or community (e.g., for the public Learning Registry community, the policy is the terms of service for the community, `http <http://www.google.com/url?q=http%3A%2F%2Fwww.learningregisrty.org%2Ftos%2F&sa=D&sntz=1&usg=AFQjCNG3rD84JmiZzviK-iAYdu4QE0NbrQ>`_://`www <http://www.google.com/url?q=http%3A%2F%2Fwww.learningregisrty.org%2Ftos%2F&sa=D&sntz=1&usg=AFQjCNG3rD84JmiZzviK-iAYdu4QE0NbrQ>`_.`learningregisrty <http://www.google.com/url?q=http%3A%2F%2Fwww.learningregisrty.org%2Ftos%2F&sa=D&sntz=1&usg=AFQjCNG3rD84JmiZzviK-iAYdu4QE0NbrQ>`_.`org <http://www.google.com/url?q=http%3A%2F%2Fwww.learningregisrty.org%2Ftos%2F&sa=D&sntz=1&usg=AFQjCNG3rD84JmiZzviK-iAYdu4QE0NbrQ>`_/`tos <http://www.google.com/url?q=http%3A%2F%2Fwww.learningregisrty.org%2Ftos%2F&sa=D&sntz=1&usg=AFQjCNG3rD84JmiZzviK-iAYdu4QE0NbrQ>`_/)

  - <sword:treatment> and <sword:service> elements SHALL be omitted.

**API**

    GET <node-service-endpoint-url>/swordservice

    HTTP Headers

                X-On-Behalf-Of: [on-behalf-of-user]

    Results XML

        Well formed XML instance document that conforms to the SWORD 1.3 specification.

                        <?xml version="1.0" encoding="utf-8"?>

                        <service xmlns="http://www.w3.org/2007/app"

                 xmlns:atom="http://www.w3.org/2005/Atom"

                xmlns:sword="http://purl.org/net/sword/"

                xmlns:dcterms="http://purl.org/dc/terms/">

             <sword:version>1.3</sword:version>

                        <sword:verbose>true</sword:verbose>

                        <sword:noOp>true</sword:noOp>

                         <workspace>

                 <atom:title>...</atom:title>

                 <collection href="..." >

                  <atom:title>...</atom:title>

                  <accept>application/json</accept>

                 <sword:mediation>true</sword:mediation>

                  <dcterms:abstract>...</dcterms:abstract>

                                 <sword:collectionPolicy>...</sword:collectionPolicy>

                 </collection>

              </workspace>

                        </service>

**SWORD****: ****swordservice**

    // return the service document

    Build XML results document

    EMIT the Atom Pub and SWORD namespace declarations

    EMIT the required elements

                <sword:version>1.3</sword:version>

                <sword:verbose>true</sword:verbose>

                <sword:noOp>true</sword:verbose>

    EMIT the workspace elements

        <workspace>

            <atom:title>community_name or community_id from the *network* *community*                 *description* *data* *model*<atom:title>

    IF the [on-behalf-of-user] is permitted to publish to the node

        THEN EMIT the collection elements

            <collection

                href="URL of the network node">

                     <atom:title>node_name or node_id from the *network* *node* 

                                *description* *data* *model*</atom:title>

                  <accept>application/json</accept>

                 <sword:mediation>true</sword:mediation>

                  <dcterms:abstract>node_description from the *network* *node*                             *description* *data* *model*</dcterms:abstract>

                                <sword:collectionPolicy>Policy URL</sword:collectionPolicy>

                 </collection>

    Complete XML elements

        </workspace>

                </service>


"""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.2o7qqzkocz2j:

**Create** **a** **Resource**
"""""""""""""""""""""""""""""""""""""""""""""""""""

    in a future draft of the specification

**API**

    POST <node-service-endpoint-url>/swordpub

    HTTP Headers

    Results XML

**SWORD****: ****swordpub**

    // pseudo code

**Service** **Description**

    {

         "doc_type":        "service_description",    

         "doc_version":        "0.20.0",

         "doc_scope":        "node",

         "active":        true,

         "service_id":        "<uniqueid>",        

         "service_type":        "publish",

     "service_name":    "SWORD APP Publish V1.3",

    "service_description":    "Service to publish resource description documents to a node using the SWORD 1.3 protocol",        

     "service_version":    "0.10.0",

     "service_endpoint":    "<node-service-endpoint-URL>",

     "service_auth":                // service authentication and authorization descriptions

     {

     "service_authz":    ["<authvalue>"],     // authz values for the service

     "service_key":        <T/F>,        // does service use an access key            

     "service_https":    <T/F>        // does service require https

     },

      "service_data":

         {

     "version":        "1.3"

     }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
Appropriate values for the service_data elements SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.


"""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.rfe7ga-6sbjly:

**Basic** **Delete** **Service**
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

The basic delete service "deletes” an instance of a resource data description document (or a set of documents) directly from a node in a resource distribution network.


Each resource data description document identified in the supplied set is deleted independently.
In addition to the overall service return indicating status, there SHALL be one returned object per resource data description document, aligned 1:1 to the documents identified in the supplied resource data description document array, indicating deletion of the resource data description document.

The service MAY implement different deletion policies:

- *ignore* -- the deletion SHALL be acknowledged but the document is not deleted.

- *mark* -- the status of the document is changed to indicate that it has been deleted.
  The document SHALL NOT be returned by any access service.

- *delete* -- the document SHALL be deleted.
  What “deleted” means is dependent on the underlying implementation.

- *purge* -- the service SHALL, at some point, remove deleted documents.

*NB*: There are no restrictions on the size of a batch publish document set, either in the number of elements or the total size of the HTTP message.
An implementation SHALL indicate any size limits in the service description.

*NB*: Only the owner of a document may delete it.

*NB*: A mechanism to delete all resource data description documents associated with a single resource identifier (resource locator) is not provided since these resource data description documents may have different owners.

*NB*: The deletion process SHALL be consistent with the `Resource <https://docs.google.com/a/learningregistry.org/document/d/1NxS_QSxuTemFOi0uduUDvX69m8_AwHPUM2HmnI-tyuc/edit?hl=en_US#heading=h.a9luwl-3jrses>`_ `Data <https://docs.google.com/a/learningregistry.org/document/d/1NxS_QSxuTemFOi0uduUDvX69m8_AwHPUM2HmnI-tyuc/edit?hl=en_US#heading=h.a9luwl-3jrses>`_ `Persistence <https://docs.google.com/a/learningregistry.org/document/d/1NxS_QSxuTemFOi0uduUDvX69m8_AwHPUM2HmnI-tyuc/edit?hl=en_US#heading=h.a9luwl-3jrses>`_ policy.

**API**

        POST <node-service-endpoint-URL>/delete

            

        Arguments:

            None

        Request Object:                    // list of resource data descriptions to delete

                {"request_IDs":

                [                    // array of

                 doc_ID                    // resource data description document ID

                                    // required

            ]}

        Results Object:

                {

                 "OK":        boolean,        // T if successful

                 "error":        "string",            // text describing global error

                                    // present only if NOT OK

                "document_results":

                [                    // array of per document results

                 {

                 "doc_ID":    "string",            // ID of the document

                 "OK":        boolean,            // T if document was deleted

                 "error":        "string"            // text describing deletion error

                                    // present only if NOT OK

                 }

                         ]

                }

        Return Codes:

            200

            500

**Basic** **Delete**

        // Obtain the resource data description document for each supplied ID

        FOR EACH *resource* *data* *description* document ID

                Put the *resource* *data* *description* document ID in the results object

                IF the document does not exist

                    THEN 

                                OK := FALSE

                                error := "document doesn’t exist"

                                SKIP

        IF the document has been deleted

                    THEN 

                                OK := FALSE

                                error := "document already deleted

                                SKIP    

        // otherwise delete

        OK := TRUE

                CASE delete_action

                    ignore:

                                NO OP

                    mark: 

                                set a flag on the document that it is deleted // ACTIVE := FALSE

                    delete: 

                                perform a system-level delete // whatever "delete" means

                    purge: 

                                perform a system-level delete // whatever "delete" means

                                trigger system level purge // may run at some later time

**Service** **Description**

    {

         "doc_type":        "service_description",    

         "doc_version":        "0.20.0",

         "doc_scope":        "node",

         "active":        true,

         "service_id":        "<uniqueid>",        

         "service_type":        "delete",

         "service_name":    "Basic Delete",

        "service_description":    "Delete Service",        

         "service_version":    "0.10.0",

         "service_endpoint":    "<node-service-endpoint-URL>",

     "service_auth":                // service authentication and authorization descriptions

     {

     "service_authz":    ["<authvalue>"],     // authz values for the service

     "service_key":        <T/F>,        // does service use an access key            

     "service_https":    <T/F>        // does service require https

     },

         "service_data":

         {

         "delete_action":    "string",        // fixed vocabulary ["ignore", "mark", "delete", "purge"]

                            // ignore -- ignore the delete request

                            // mark -- mark the document as deleted

                            // delete -- delete the document from the document store

                            // purge -- purge the document

     "doc_limit":        integer,         // specify the maximum number of documents in a batch

     "msg_size_limit":    integer         // specify the maximum message size

     }

    }

When the service is deployed at a node, appropriate values for the placeholders (service_id, service_endpoint, service_auth) SHALL be provided.
Appropriate values for the service_data elements SHALL be provided.
The descriptive values (service_name, service_description) MAY be changed from what is specified herein.


"""""""""""""""""""""""""""""""""""""""""

.. _h.e1519o-y653zc:

**Change** **Log**
"""""""""""""""""""""""""""""""""""""""""

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                                                                                   |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document.`Archived <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ `copy <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ (V 0.24.0) |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V PS:0.49.0)                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | TBD      | DR         | Renumber all document models and service documents. Added node policy to control storage of attachments (default is stored). Archived copy location TBD. (V PS:0.50.0)                                                                                                                       |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Logging/tracking emit as paradata to services. Deprecate node_timestamp. Details of attachments on publish, obtain, harvest.Archived copy location TBD. (V PS:x.xx.x)                                                                                                                        |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. _h.tph0s9vmrwxu:

**Working** **Notes** **and** **Placeholder** **Text**
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

.. role:: deprecation

.. role:: deletions

.. role:: changes
