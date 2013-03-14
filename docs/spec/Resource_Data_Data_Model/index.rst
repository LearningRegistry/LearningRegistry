


===============================================================================
Resource Data Data Model: Learning Registry Technical Specification V RM:0.50.1
===============================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.

:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.


.. toc


This document is part of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It describes the model of resource data that is transported through the network.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References

- :doc:`Resource Distribution Network Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Identity, Trust, Authentication, Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Services <../Services_and_APIs/index>` including :doc:`Distribution <../Distribution_Services/index>`, :doc:`Publish <../Publish_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Broker <../Broker_Services/index>`, :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that specific criteria for the Network Model are presented in the :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part.



.. _Resource Data Data Models:

-------------------------
Resource Data Data Models
-------------------------

The resource distribution network and its nodes process and distribute **resource** **data** (e.g., network messages about resources, metadata, paradata, etc.).
Producer edge nodes publish resource data to a node of the network; the resource distribution network moves it to other nodes, and consumer edge nodes pull resource data for external use from nodes.

All data models MAY be extended with additional elements.
The name of any extension element SHALL begin with the characters "X\_" designating an extension element.
Any document that includes any element that is not is the defined data model or is not an extension element is non conforming and SHALL be rejected by any service.

All data models have a named attribute that is a “type” element (doc_type).
The data model description specifies the literal value for this element for all instances of each type of document.

All data models have a named attribute that is a “version” element (doc_version).
The data model description specifies the literal value for this element for all document instances.

Additional constraints on attributes values are detailed in :ref:`Data <Data Model Attributes>` :ref:`Model <Data Model Attributes>` :ref:`Attributes <Data Model Attributes>`.






Resource Data Description Data Model
""""""""""""""""""""""""""""""""""""

The data model describing resources, metadata, paradata, etc., that is distributed by the resource distribution network.
The data model MAY be extended with additional optional, mutable elements that describe a resource and have a character string value space.
The name of such an element SHALL begin with the characters "resource\_".
Once the data model has been instantiated the value of an immutable element SHALL NOT change.
Other values MAY be changed only by the owner of the document.

::

    {

        "doc_type": "resource_data",
                                        // the literal "resource_data"
                                        // required, immutable

        "doc_version": "0.49.0",
                                        // the literal for the current version -- "0.49.0"
                                        // required, immutable
                                        // general elements about the submission

        "doc_ID": "string",
                                        // unique ID for this resource data description document
                                        // unique within scope of the LR
                                        // immutable
                                        // user optional, required for storage
                                        // system generated when publishing
                                        // the document if not provided

        "resource_data_type": "string",
                                        // open (best practices) vocabulary
                                        // ["metadata", "paradata", "resource", "assertion", ...]
                                        // required, immutable

        "active": boolean,
                                        // is the resource data description document active
                                        // required, mutable from T to F only
                                        // information about the submission, independent of the resource data

        "identity": { 
                                        // identity and curation

            "submitter_type": "string",
                                        // fixed vocabulary ["anonymous", "user", "agent"]
                                        // required, immutable
                                        // "anonymous" -- submitter is unknown
                                        // "user" -- submitter is a user or has a user identity
                                        // "agent" -- submitter is an agent, e.g., a repository, LMS
                                        // or an organization

            "submitter": "string",
                                        // identity of the submitter of the resource data
                                        // required, immutable
                                        // use "anonymous" for type "anonymous"

            "curator": "string",
                                        // identity of the curator of the resource data description
                                        // who manages the resource data description
                                        // optional

            "owner": "string",
                                        // identity of the owner of the resource
                                        // who owns what is referenced in the resource locator
                                        // optional

            "signer": "string" 
                                        // identity of key owner used to sign the submission
                                        // optional
        },

        // submission and distribution workflow information
        "submitter_timestamp": "string",
                                        // submitter-created timestamp
                                        // time/date encoding
                                        // optional

        "submitter_TTL": "string",
                                        // submitter statement of TTL of validity of submission
                                        // time/date encoding
                                        // optional

        "publishing_node": "string",
                                        // node_id of node where injected into the network
                                        // required
                                        // provided by the initial publish node (not distribution)

        "update_timestamp":    "string",       
                                        // timestamp of when published to the network
                                        // of latest update
                                        // time/date encoding
                                        // required
                                        // provided by the initial publishing node
                                        // not by a distribution node
                                        // ▲ Added back, inadvertently removed from previous version of spec.

        "node_timestamp": "string",
                                        // timestamp of when received by the current node
                                        // time/date encoding
                                        // required
                                        // provided by the current distribution node
                                        // NOT distributed to other nodes
                                        // ▲ Removed from deprecation

        "create_timestamp": "string",
                                        // timestamp of when first published to the network
                                        // independent of updates
                                        // time/date encoding
                                        // required, immutable
                                        // provided by the initial publishing node on first publish
                                        // not by a distribution node or not an update
        "TOS": { 
                                        // terms of service
            "submission_TOS": "string",
                                        // agreed terms of service by submitter
                                        // required

            "submission_attribution": "string" 
                                        // attribution statement from submitter
                                        // optional
        },

        "do_not_distribute": "string",
                                        // system provided key-value pair
                                        // optional

        "weight": "integer",
                                        // submitter assigned weight (strength)
                                        // -100:100
                                        // optional

        "digital_signature": { 
                                        // digital signature of the submission, optional

            "signature": "string",
                                        // signature string, required
            "key_location": ["string"],
                                        // array of public key locations,, required

            "signing_method": "string"
                                        // fixed vocabulary ["LR-PGP.1.0"]
                                        // required
        },

        // information about the resource, independent of the resource data
        "resource_locator": "string",
                                        // unique locator for the resource described
                                        // SHALL resolve to a single unique resource
                                        // ▲ required unless "replaces" is non-empty indicating deletion. 

        "keys": ["string"],
                                        // array of hashtag, keyword value list used for filtering
                                        // optional

        "resource_TTL": integer,
                                        // TTL from resource owner for the resource itself, in days
                                        // optional
                                        // the actual resource data description elements
                                        // these elements are optional as a block if the submission is a resource

        "payload_placement": "string",
                                        // fixed vocabulary ["inline", "linked", "attached"]
                                        // "inline" -- resource data is in an object that follows
                                        // "linked" -- resource data is at the link provided
                                        // "attached" -- resource data is in an attachment
                                        // ▲ required unless "replaces" is non-empty indicating deletion. 

        "payload_schema": ["string"],
                                        // array of schema description/keywords
                                        // for the resource data
                                        // ▲ required if "replaces" is non-empty
                                        // defined :ref:`metadata schema values<h.ykraw8-ientp5>`
                                        // defined :ref:`paradata schema values<h.5bpp9l-ncbjqy>`

        "payload_schema_locator": "string",
                                        // schema locator for the resource data
                                        // optional

        "payload_schema_format": "string",
                                        // schema MIME type
                                        // optional

        "payload_locator": "string",
                                        // locator if payload_placement value is "linked"
                                        // required if "linked", otherwise ignored

        "resource_data": <the resource data object>,
                                        // the actual inline resource data
                                        // the resource data itself (resource_metadata, paradata)
                                        // maybe a JSON object, or
                                        // a string encoding XML or some other format, or
                                        // a string encoding binary
                                        // ▲ required if "inline" or "replaces" is non-empty indicating deletion, otherwise ignored


        "replaces": ["string"],
                                        // A list of doc_ID that refer to resource data that this resource data should replace
                                        // optional
                                        // ▲ new field handilng replacements.

        "X_xxx": ? ? ? ? ? 
                                        // placeholder for extensibility, optional
    }


JSON Schema
===========
Following is Resource Data Description Data Model described using `JSON Schema V3 <http://tools.ietf.org/html/draft-zyp-json-schema-03>`_.
Instances of the data model describing resources MUST validate against one of the following schemas:

    - file\:lr/schema/v_0_49/inline_resource_data.json : a data model where the resource data is included in the instance inline.
    - file\:lr/schema/v_0_49/linked_resource_data.json : a data model where the resource data is linked externaly.
    - file\:lr/schema/v_0_49/deleted_resource_data.json : a data model that indicates that a previously published inline or linked data model instance should be removed from the node.
    - file\:lr/schema/v_0_49/resource_data.json : a union of the previous schemas

file\:lr/schema/v_0_49/resource_data.json
-----------------------------------------

.. literalinclude:: ../../../LR/lr/schema/v_0_49/resource_data.json
    :language: javascript



file\:lr/schema/v_0_49/inline_resource_data.json
------------------------------------------------

.. literalinclude:: ../../../LR/lr/schema/v_0_49/inline_resource_data.json
    :language: javascript



file\:lr/schema/abstract_inline_resource_data.json
--------------------------------------------------

.. literalinclude:: ../../../LR/lr/schema/abstract_inline_resource_data.json
    :language: javascript


file\:lr/schema/v_0_49/deleted_resource_data.json
-------------------------------------------------

.. literalinclude:: ../../../LR/lr/schema/v_0_49/deleted_resource_data.json
    :language: javascript


file\:lr/schema/v_0_49/linked_resource_data.json
------------------------------------------------

.. literalinclude:: ../../../LR/lr/schema/v_0_49/linked_resource_data.json
    :language: javascript



file\:lr/schema/abstract_linked_resource_data.json
--------------------------------------------------

.. literalinclude:: ../../../LR/lr/schema/abstract_linked_resource_data.json
    :language: javascript



file\:lr/schema/abstract_resource_data.json
-------------------------------------------

.. literalinclude:: ../../../LR/lr/schema/abstract_resource_data.json
    :language: javascript



Timestamp values for update_timestamp, :changes:`▲ node_timestamp`, and create_timestamp SHALL be UTC 0.

*Open* *Question*: Is there a use case that requires create_timestamp?

*Open* *Question*: Is locator sufficient, or do we still need an ID for the resource?

*NB*: The doc_ID is not required when a user creates a resource data description document.
If missing, it SHALL be provided by a publishing service when the document is first published.

*NB*: Need to agree on the conventions for valid submitter, owner and TOS strings.

*NB*: Separating owner from submitter enables 3rd party submissions.

*NB*: If the key owner is not included in the digital signature, the submitter is assumed to be the key owner.

*NB*: Separating the key owner from the submitter enables 3rd party signing of submissions.

*NB*: The signing mechanism is described under :ref:`Identity <Identity and Digital Signatures>` :ref:`and <Identity and Digital Signatures>` :ref:`Digital <Identity and Digital Signatures>` :ref:`Signatures <Identity and Digital Signatures>`.

*NB*: Providing the signing method enables different signing algorithms.

*NB*: The supplied resource_locator SHALL be a unique ID within the scope of the Learning Registry and SHALL resolve to a single resource from which someone may uniquely access the resource.
The resource_locator is used to correlate multiple resource data descriptions about a single resource.
Thus the locator needs to be specific to the resource.

*NB*: A resource data description document contains only one set of resource data (metadata, paradata).

*NB*: The weight is used let the submitter assign a confidence level to the data.

*NB*: To submit data only for a resource (no metadata or paradata), the payload attributes MAY be omitted.

*NB*: There is currently no mechanism to update the resource_* attributes without resubmitting the metadata or paradata about the resource.
This is consistent with document-oriented transactional atomicity.

*NB*: There are no restrictions on the actual resource data.
The format and encoding are based on the defined payload_schema and payload_schema_format values.

*NB*: Best practices of how to use the resource_* attributes and how to encode values are not provided.

*NB*: Some elements MAY be mapped to DC terms or LOM schema elements.

+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| **Resource** **Data** **Description** | **Dublin** **Core**              | **IEEE** **LOM**                                                                                     |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_data_owner                   |                                  | 3.3.2: LifeCycle.Contribute.Entity when 2.3.1: LifeCycle.Contribute.Role has a value of “Submitter.” |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_description                  | dc:description                   | 1.4: General.Description                                                                             |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_format                       | dc:format                        | 4.1: Technical.Format                                                                                |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_language                     | dc:language                      | 1.3: General.Language                                                                                |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_locator                      | dc:ID                            | 1.1: General.Identifier or 4.3: Technical.Location                                                   |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_owner                        | dc:publisher                     | 2.3.2: LifeCycle.Contribute.Entity when 2.3.1:LifeCycle.Contribute.Role has a value of “Publisher.”  |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_rights                       | dc:rights                        | 6.3: Rights.Description                                                                              |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_relationship                 | dc:resource refinement qualifier | 7.1: Relation.Kind                                                                                   |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_subject                      | dc:subject                       | 1.5: General.Keyword                                                                                 |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_title                        | dc:title                         | 1.2: General.Title                                                                                   |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_TTL                          |                                  |                                                                                                      |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| resource_type                         | dc:type                          | 5.2: Educational.LearningResourceType                                                                |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+
| related_resource                      | dc:resource                      | 7.2.1: Relation.Identifier.Identifier                                                                |
+---------------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------+





Metadata Formats
""""""""""""""""

The metadata in a resource data description MAY be defined using any metadata standard.
Metadata documents SHALL include the reference to the defining standard or schema.
The following list of schema values SHALL be used to refer to common schemata.
Implementations MAY extend this list.

+---------------------------+--------------------------+
| **Metadata** **Standard** | payload_schema **value** |
+---------------------------+--------------------------+
| Dublin Core 1.1           | "DC 1.1"                 |
+---------------------------+--------------------------+
| IEEE LOM 2002             | "IEEE LOM 2002"          |
+---------------------------+--------------------------+
| OAI\-PMH Dublin Core      | "oai_dc"                 |
+---------------------------+--------------------------+

Attached and linked metadata SHALL include appropriate schema definitions and schema locators in the metadata file.


*NB*.
There is currently no machine-readable list of schemata.
Such a list could be defined in additional network description documents.

Inline metadata SHALL be encoded in JSON structure or as a single JSON string wrapping the entire metadata document.

JSON encodings of metadata schemata (primarily for inline resource data) will be provided in a future draft of the specification.






Paradata Formats
""""""""""""""""

The paradata in a resource data description MAY be defined using any paradata standard.
Paradata documents SHALL include the reference to the defining standard or schema.
The following list of schema values SHALL be used to refer to common schemata.
Implementations MAY extend this list.

+---------------------------+--------------------------+
| **Paradata** **Standard** | payload_schema **value** |
+---------------------------+--------------------------+
|                           |                          |
+---------------------------+--------------------------+

Attached and linked paradata SHALL include appropriate schema definitions and schema locators in the paradata file.


*NB*.
There is currently no machine-readable list of schemata.
Such a list could be defined in additional network description documents.

Inline paradata SHALL be encoded in JSON structure or as a single JSON string wrapping the entire paradata document.

JSON encodings of paradata schemata (primarily for inline resource data) will be provided in a future draft of the specification.






Resource Data
"""""""""""""

The resource data SHALL be maintained in a set of documents stored at each node in the network.

- Each node MAY store one or more instances of the `resource data description documents <Resource Data Description Data Model>`_.
  All document instances stored at a node SHALL be unique.
  A document MAY be replicated at many nodes.

Any resource description document with a "do_not_distribute" key is consdered to be a local document stored only at the node (independent of the value of the key).
A document with this key-value pair SHALL be unconditionally rejected during publishing or distribution.

Additional types of resource data documents (documents that differ in purpose from resource data description documents) MAY be defined, but SHALL be defined as unique per node.
Other types of resource data description documents SHALL NOT be defined and SHALL NOT be replicated.
Other organizational classifications SHALL NOT be used.
*NB*: These constraints are meant to restrict placing resource data in multiple different databases.


Tombstones
""""""""""

A tombstone is node local document that acts a terminal marker for an RD3.  It SHALL be the only allowed mutability of a RD3. A tombstone MUST NOT be distributed to other nodes.

The data model for a tombstone SHALL adhere to the following `JSON Schema <http://tools.ietf.org/html/draft-zyp-json-schema-03>`_:


JSON SCHEMA
===========

file\:lr/schema/v_0_49/tombstone.json
-------------------------------------

.. literalinclude:: ../../../LR/lr/schema/v_0_49/tombstone.json
    :language: javascript


*NB*: ALL harvest services SHOULD be updated to exclude tombstones.
*NB*: Any harvest service MAY be updated to allow explicit request for tombstone by “doc_ID”. It is RECOMMENDED this feature only be available via Basic Harvest and Obtain.




----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                                                                                                                                   |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document.`Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V RM:0.49.0)                                                                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | TBD      | DR         | Renumber all document models and service documents. Added node policy to control storage of attachments (default is stored). Add page size as service doc setting with flow control.Archived copy location TBD. (V RM:0.50.0)                                                                                                                |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Assertion (relation/sameas) and trust documents.Archived copy location TBD. (V RM:x.xx.x)                                                                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130226 | JK         | Convert to RestructuredText formatting.  Adding model changes Replacement Documents and Tombstones per `Amendment (V 0.3) <https://docs.google.com/document/d/1JpwEQ4J6ruQUe502K4XzLnWqvC5L67vjasTTFKQo9e8/edit>`_. `Archived Copy (V RM:0.49.0) <https://docs.google.com/document/d/1zD0PUvQB0g-JpdbcioDL7WZByGtP79jbf0OoyQLISDM/edit>`_    |
|             |          |            | Added missing field update_timestamp which got removed from some previous version inadvertently. node_timestamp removed from deprecation.                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+





----------------------------------
Working Notes and Placeholder Text
----------------------------------

