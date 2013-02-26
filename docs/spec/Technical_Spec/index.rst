
.. _h.yz89tlej50:

==================================================
Learning Registry Technical Specification V 0.49.0
==================================================

**Draft in Progres**.
**See the  :ref:`Change Log <h.q7vwu59mjki6>` for links to prior stable versions**.

:changes:`**Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with** ▲.`

:deletions:`**Significant deletions are shaded.**`

:deprecation:`**Features to be deprecated in a future version are shaded and indicated with** ▼.`

**This document is the whole of the Learning Registry Technical Specification.**


.. _h.c7bnrod3e0k:

------------------------------------
Technical Specification Introduction
------------------------------------

This document provides the technical specification for the Learning Registry.
It specifies the network model, data models and APIs.
It does not specify policy-based operational procedures or the instantiation or deployment of the Learning Registry.
It does not specify internal data models or internal APIs.
The specification focuses on the APIs used by external agents and the data models and APIs required for overall operations of a network and general interoperability of external agents.
While targeted at a document-oriented infrastructure, the specification itself is independent of any particular toolset.
The document is currently a work in progress; its structure, organization and content are subject to change.


.. _h.mus9vqexu2or:

--------------------------------
Technical Specification Contents
--------------------------------

.. toctree::
    :maxdepth: 2
    :numbered:

    ../General_Matter/index
    ../Resource_Distribution_Network_Model/index
    ../Resource_Data_Data_Model/index
    ../Identity_Trust_Auth_and_Security/index
    ../Data_Model_and_API_Attributes_and_Behaviors/index
    ../Services_and_APIs/index
    ../Distribution_Services/index
    ../Publish_Services/index
    ../Access_Services/index
    ../Broker_Services/index
    ../Mgmt_Admin_and_Discovery_Services/index
    ../Operations/index


.. _h.q7vwu59mjki6:

----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.

*NB*: Updates and edits may not results in a version update.

*NB*: See the individual partsg of the Technical Specification for specific changes to that part.

+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.10.0      | 20110117 | DR         | Initial public release (lacks resource data model). `Archived copy <https://docs.google.com/document/d/1mJhXzZTwF7S8lfuV0j0axJJCahLDtGCZtCaeeB81x7Q/edit?hl=en>`_ (V 0.10.0)                                                                                                                                                                                                                                                                                                                                                                             |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.15.0      | 20110222 | DR         | Added filtering. Added basic harvest. Added resource data model. Added basic delete. `Archived copy <https://docs.google.com/document/d/1LGwYxEqSRe4tdV4at6x8WWXI7nfXMGoY4x3kO5UqIgY/edit?hl=en>`_ (V 0.15.0)                                                                                                                                                                                                                                                                                                                                            |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.16.0      | 20110310 | DR         | Added OAI\-PMH harvest. Obtain extended to support by doc_ID or by resource_ID/locator access. Documented Obtain. Basic Harvest extended to support doc_ID or by resource_ID/locator access for GetRecord.  `Archived copy <https://docs.google.com/document/d/1em8LdbX9tkvB66yqoe96MNKdAWTyt_lMSQjyzAREYWg/edit?hl=en>`_ (V 0.16.0)                                                                                                                                                                                                                     |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.17.0      | 20110415 | DR         | Clarified that services are optional, described operational requirements to provision services. Revised XSD to support OAI\-PMH harvest by resouce_ID. Clarified times are UTC 0. Clarified distributeAPI to uncouple it from other APIs. Add ToS checks to distribute and publish. Update reource doc to include ToS attribution. Added SWORD API. `Archived copy <https://docs.google.com/document/d/1UyN_cacpCz4Xj8G4XEGcnzAC57hS3UZyng6aJGtvXdM/edit?hl=en>`_ (V 0.17.0)                                                                             |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.20.0      | 20110422 | DR         | Added digital signature k\-v pairs to resource documents. Added public key k\-v pairs to all description documents. Updated network and node policy descripitons. Added signature, trust, ... verification to publish. Added identity section. Defined ALL behavior for obtain for size limited. Defined returning spec JSON vs. stored JSON for obtain and harvest. Authn (none, basic, SSH, Oauth, ...). Authz (access keys). `Archived copy <https://docs.google.com/document/d/1wd_mwuFubtZsUS6p9_nyAgabzldf1bfhITN3sRlw7sc/edit?hl=en>`_ (V 0.20.0) |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.21.0      | 20110706 | DR         | Updated how to sign documents. Modified resource document description to restructure identity. Added JSONP to APIs. Obtain flow control (to be moved to a common location to add to other APIs).  `Archived copy <https://docs.google.com/document/d/1jREjZ9N9Bzifn_kWy2rmGNe6E1nx3B7vmG6k_Cjg6n8/edit?hl=en_US>`_ (V 0.21.0)                                                                                                                                                                                                                            |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.22.0      | 20110708 | DR         | Made resource doc type an open vocabulary. Added trust weight. Added requirement that a service document exist for a service. `Archived copy <https://docs.google.com/document/d/1SW3ILArsGOOp1MmMzUnRuHw8R-JZfj7j79-w5sHDzT0/edit?hl=en_US>`_ (V 0.22.0)                                                                                                                                                                                                                                                                                                |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.23.0      | 20110921 | DR         | Added k\-v pair to mark documents as non distributable and process to block publication and distribution (take down process is policy, not part of the specification. Added checks on max doc size. Indicated that node time stamp is to be depricated. Indicated services to be deprecated. Documented obtain get interface. `Archived copy <https://docs.google.com/document/d/1fRbDpM0BKvNc4WzDzX0pNUpfPtFAsKpKGnOyRhRok-8/edit?hl=en_US>`_ (V 0.23.0)                                                                                                |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.24.0      | 20110921 | DR         | Remove deprecated servcies (query, SRW, Sitemap). `Archived copy <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ (V 0.24.0)                                                                                                                                                                                                                                                                                                                                                                            |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| NA          | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document.Archived copy NA                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Changed license from OWA CLA 0.9 to OWA CLA 1.0. Added GM section on versioning.Archived copy location TBD (V 0.49.0)                                                                                                                                                                                                                                                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Add service code version to service documents (extracted from code on install). Renumber all document models and service documents. Added node policy to control storage of attachments (default is stored). Add page size as service doc setting with flow control.Archived copy location TBD (V x.xx.x)                                                                                                                                                                                                                                                |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | ToS attribution output to OAI. Harvest flow control. Flow control to OAI. Logging/tracking emit as paradata to services. Assertion (relation/sameas) and trust documents. Deduplication service. RESTful APIs. Details of attachments on publish, obtain, harvest. Depricate node_timestampArchived copy location TBD (V x.xx.x)                                                                                                                                                                                                                         |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | XXXArchived copy location TBD (V x.xx.x)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


.. _h.glq08ftdxizl:

----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
