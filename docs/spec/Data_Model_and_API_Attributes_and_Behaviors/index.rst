


====================================================================================================
Data Model and API Attributes and Behaviors: Learning Registry Technical Specification V RQ:0.50.1
====================================================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.

:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.


This document is part of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It describes common requirements for all APIs and data models.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General <../General_Matter/index>` :doc:`Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References,

- :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>`

- :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Services <../Services_and_APIs/index>` including :doc:`Distribution <../Distribution_Services/index>`, :doc:`Publish <../Publish_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Broker <../Broker_Services/index>`, :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that information from this part of the Technical Specification applies to all services and data models.





""""""""""""""""""""""""""""""""""""""""""""""""""
Common Data Model and API Attributes and Behaviors
""""""""""""""""""""""""""""""""""""""""""""""""""

The definition of several common attributes shared across all data models and APIs, along with common API behaviors are specified here as a single point of specification.
In case of a discrepancy, the definition here SHALL take precedence over the definition elsewhere in this specification.



.. _Data Model Attributes:

'''''''''''''''''''''
Data Model Attributes
'''''''''''''''''''''





-----------
Identifiers
-----------

Most data models include one or more *identifiers*.
An identifier SHALL be unique within a defined scope or context.
Unless otherwise specified, the scope for all identifiers SHALL be all implementations of the Learning Registry.
Unless otherwise specified by an implementation, an identifier SHALL conform to ISO/IEC 11578:1998, ISO/IEC 9834-8, RFC 4122, and SHOULD use Version 5 (SHA-1 Hash).
These specifications standardize the generic OSF DCE UUID.
As a data type, an identifier is commonly encoded as a string.

*NB*: What is called an identifier in a data model is more precisely just a label.
The use of the label to identify an instance of the data model within the scope or context of the Learning Registry makes it an identifier (within that scope).

*NB*: For many items, the scope could be all implementations of the Learning Registry within one network 

community.
Extending the scope to all implementations is an intentional simplification.

*Open* *Question*: UUID Version 1 (MAC Address) Version 5 (SHA-1 Hash)?





--------------------------------
Strings and Internationalization
--------------------------------

All character strings SHALL support full UTF-8 encoding of Unicode character representation.

*NB*: JSON strings default to UTF-8 encoding.
ECMAScript strings are UTC-16.





-------------
Time and Date
-------------

The format for all times and dates SHALL conform to ISO 8601-2004. All encoded dates and times SHALL  be UTC 0. All *stored* times SHALL be expressed to at least second precision.
More precise values MAY be used.

Unless specified elsewhere, the JSON encoding of a time and date SHALL be a single string that is the complete, extended ISO 8601-2004 format, e.g., "YYYY-MM-DDThh:mm:ss.sZ" The string SHALL have all of these elements and separators and MAY have any precision of decimal fraction of a second.

*NB*: The above notation follows ISO 8601-2004, and the underscore on the decimal fractional portion of second implies any number of digits (zero or more) may follow the decimal point.

*NB*: Some data models and APIs MAY place additional restrictions on times and dates, including requiring less precision (e.g., days only) in arguments and results.






''''''''''''''''''''''''''''
API Attributes and Behaviors
''''''''''''''''''''''''''''

Description here about RESTful APIs, CoolURIs, Context negotiation, application/JSON vs text/plain

HTTP requests SHALL use HTTP 1.1. Communications MAY use TLS.

HTTP requests SHOULD include a CONTENT-TYPE header.
Unless noted, the header SHOULD be 

CONTENT-TYPE: application/JSON

HTTP responses SHOULD include a CONTENT-TYPE header.
Unless noted, the header SHOULD be CONTENT-TYPE: text/plain; charset=utf=8

Unless noted, all APIs that return JSON via an HTTP GET request SHALL support return of JSON-P to enable processing of the results by a ECMA-Script client.
GET requests SHALL support an optional jsonp argument.
If the jsonp argument is present, the API SHALL return the result padded into the function named in the jsonp argument.






--------------------------------
Service Instantiation Validation
--------------------------------

A service at a node SHALL verify that a valid *service description document* exists for the service.
If the service description document does not exist, is invalid, or indicates that the service is not active, the service SHALL return an HTTP status code.

If the service description document does not exist, the status code SHALL be 501 and the response SHALL include the statement: "Service not implemented".

If the service description document is not valid, the status code SHALL be 501 and the response SHALL include the statement: "Service misconfigured".

If the service description document indicates that the service is not active, the status code SHALL be 501 and the response SHALL include the statement: "Service is not active".

*NB*: These validation checks are performed by the service.
If the service is not instantiated at a node, the returned HTTP status code SHALL be 404.

*NB*: A service description document and installed code are both required in a valid service instantiation.
One SHOULD NOT exist without the other.





--------------------------------------------
Transactional Behaviors and Data Consistency
--------------------------------------------

Unless stated in an individual API specification, transactional atomicity SHALL BE document granularity.


Requirements for consistency of documents across multiple nodes apply only when the nodes are consistent.
Prior to, or during document distribution, documents MAY be inconsistent.

*NB*: The distribution model assumes the underlying system SHALL produce *eventual consistency*.



.. _Resource Data Validation and Publication:


----------------------------------------
Resource Data Validation and Publication
----------------------------------------

All resource data publishing and distribution services SHALL validate all documents before the document is stored at the node.

- All required fields SHALL be present.

- Only mutable fields MAY be changed in an update.

- The node SHALL reject a submission where the payload does not correspond with the declared payload.

- The node MAY validate an attached or linked payload.

- The node MAY validate an inline payload.

- Prior attachments SHALL be deleted in an update.

- Default values SHALL be filled in.

- Node-specific fields SHALL be filled in.

Resource Data Validation and Publication
========================================


::

                                        // Validate a *resource* *data* *description* document

                                        // is the submission well formed

    IF any required element is missing

        THEN

            REJECT the document

            EXIT    

                                        // changes in mutable fields are only allowed in an update

    IF submission is an update

        IF any immutable field in the new document does not match old field

            THEN

                REJECT the document

                EXIT

                                        // does the payload match the declaration

    IF payload_placement = "linked" and no payload_locator provided

        THEN

            REJECT the document

            EXIT

    IF payload_placement = "inline" and no resource_document in the submission 

        THEN

            REJECT the document

            EXIT

    IF payload_placement = "attached" and no attachment

        THEN

            REJECT the document

            EXIT

                                        // payload must match the schema and validate

    IF payload_schema does not correspond to resource_data_type

        THEN

            REJECT the document

            EXIT

    VALIDATE the payload

                                        // updates invalidate existing attachments

    IF submission is an update

        THEN delete any attachments

                                        // Generate the ID if required

    IF doc_ID isn’t provided

        THEN generate a doc_ID

                                        // Set local node data

    publish_node := node_id

    IF submission is an update

        THEN 

            update_timestamp := ▼:deprecation:`node`:deprecation:`_`:deprecation:`timestamp` := current time // granularity of seconds

        ELSE

            create_timestamp :=update_timestamp := ▼:deprecation:`node`:deprecation:`_`:deprecation:`timestamp` := current time

    IF frbr_level not specified

        THEN frbr_level := "copy"

 

*Open* *Question*: Should an update delete the attachments automatically, or should this be an option?



.. _Resource Data ToS, Signatures and Trust Policy Enforcement:

----------------------------------------------------------
Resource Data ToS, Signatures and Trust Policy Enforcement
----------------------------------------------------------

All resource data publishing services and resource data distribution services MAY apply ToS, digital signature and submitter identity checks to resource data.

- The node MAY reject an anonymous submission or any other submission according to its policy.

- The node MAY reject a submission from an untrusted submitter.

- The node MAY reject a submission without a known terms of service.

- The node MAY reject a submission that is not signed.

- The node MAY reject the submission if the signature cannot be verified.

*NB*: The acceptable node policies and terms of service are not defined in this specification.
The specification requires that ToS, digital signatures and trust checks be performed according to node policies.
The outcome of those checks, and the actions taken, are governed by node, network or community-specific policies that are out of scope for this specification.

*NB*: Declared policies SHOULD be applied consistently in both publication and distribution.

*NB*: A node MAY apply other policies or MAY apply policies without declaring them in the node description.

*NB*: An implementation MAY check policies in any order.
It MAY evaluate all policies or do a short-circuit evaluation and stop when any policy violation is found.

Resource Data ToS, Signatures and Trust Policy Enforcement
==========================================================

::

                                        // Check Policies

    IF the service applies ToS checks

        AND the *resource* *data* *description* document TOS is unacceptable

        THEN // indicate ToS was rejected

            REJECT the document

            EXIT

    IF the service does not accept anonymous submissions

        AND the *resource* *data* *description* document has submitter_type=="anonymous"

        THEN // indicate submitter type was rejected

            REJECT the document

            EXIT

    IF the service validates the submitter or submitter trust

        AND the *resource* *data* *description* document submitter cannot be verified or trusted

        THEN // indicate submitter was rejected

            REJECT the document

            EXIT

    IF the service requires a signature

        AND the *resource* *data* *description* document signature not present

        THEN // indicate signature was rejected

            REJECT the document

            EXIT

    IF the service validates the signature

        AND the *resource* *data* *description* document signature cannot be verified

        THEN // indicate signature was rejected

            REJECT the document

            EXIT





------------------------------
Operational Policy Enforcement
------------------------------

All resource data publishing services and resource data distribution services MAY enforce operational policies

- The node MAY reject the size of a document as being too large according to its policy.

*NB*: Declared policies SHOULD be applied consistently in both publication and distribution.

*NB*: A node MAY apply other policies or MAY apply policies without declaring them in the node description.

*NB*: An implementation MAY check policies in any order.
It MAY evaluate all policies or do a short-circuit evaluation and stop when any policy violation is found.

Operational Policy Enforcement
==============================

::

                                        // Check Policies

    IF the service applies ToS checks

        AND the *resource* *data* *description* document TOS is unacceptable

        THEN 
                                        // indicate ToS was rejected

            REJECT the document

            EXIT



.. _Resource Data Filtering:

-----------------------
Resource Data Filtering
-----------------------

All resource data publishing services and resource data distribution services apply filters to resource data.
If a :ref:`Network Node Filter Document <Network Node Description Data Model>` is stored at a node, the filter SHALL be applied to a resource data description document before the document is stored at the node.

Either a custom filter or expression-based filters MAY be defined.
If there is a custom filter (expressed in custom code at the node), expression-based filters SHALL be ignored.
A custom filter SHOULD NOT be used when the filters can be expressed using expression-based filters.

A filter defines either the resource data documents that pass the filter (and are stored; all other resource data documents are not stored), or resource data documents that are rejected by the filter (and are not stored, all other documents are stored).

An expression-based filter contains a list of regular expressions that are used to match keywords/names in the resource data description document, and a regular expression that is used to match values for the keywords.
If the filter key matches any keyword/name in the resource data, and if any value for that key in the resource data matches the filter value, the filter is successful, i.e., for an “include” filter, the document is included; for an exclude filter, the document is “excluded”. Matching is an “or”. A successful match short circuits further matching.

The filter SHALL be applied against all top-level elements in the resource data description document.
Behavior for filtering against linked resource data, attachments or the inline resource data is not currently defined.

*NB*: Resource data filtering is in addition to the prerequisite manditory filtering of any document that contains a do_not_distribute key-value pair.

Resource Data Filtering
=======================

::

                                        // Filter a *resource* *data* *description* document

                                        // No filter test

    IF the *network* *node* *filter* *description* document does NOT exist

        THEN store the *resource* *data* *description* document 

            EXIT

                                        // Filter not active test

    IF NOT active in the *network* *node* *filter* *description* document

        THEN store the *resource* *data* *description* document

            EXIT

                                        // Use custom filter if defined

    IF custom_filter in the the *network* *node* *filter* *description* document

        THEN eval the custom filter code

            IF the code returns true 

                THEN store the *resource* *data* *description* document

                    EXIT

                                        // Expression-based filtering

                                        // Does the filter match the document

    match := F

    FOR EACH filter in the *network* *node* *filter* *description* document

        FOR EACH key/name in the *resource* *data* *description* document

        IF the filter_key REGEX matches the key/name

            IF the filter_value is NULL

                THEN match := T

                    SKIP ALL

            FOR EACH value of the key/name in the *resource* *data* *description* document

                IF the filter_value REGEX matches the value 

                    THEN match := T

                        SKIP ALL

                                        // Store or reject

    IF include_exclude 

        IF match // matches what to include

            THEN store the *resource* *data* *description* document

                EXIT

            ELSE EXIT // don’t store

        IF NOT match // doesn’t match what to exclude

            THEN store the *resource* *data* *description* document

                EXIT

            ELSE EXIT // don’t store


.. _Change Log:

----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                     |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document. `Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_     |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V RQ:0.49.0)                                                                                                      |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | TBD      | DR         | Renumber all document models and service documents. Archived copy location TBD. (V RQ:0.50.0)                                                                                                  |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | RESTful APIsArchived copy location TBD. (V RQ:x.xx.x)                                                                                                                                          |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | Coverted specification source to RestructuredText. `Archived Copy (V RQ:0.49.0) <https://docs.google.com/document/d/1p-6XFb_eBlVYiGb9fZYtcQ4Z363rjysgS2PiZLXzAyY/edit>`_                       |
+-------------+----------+------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+




----------------------------------
Working Notes and Placeholder Text
----------------------------------

- Flow control consistency

- How does a service find its service doc

.. role:: deprecation

.. role:: deletions

.. role:: changes
