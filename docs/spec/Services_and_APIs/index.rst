


========================================================================
Services and APIs: Learning Registry Technical Specification V SA:0.50.1
========================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.

:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.

This document is part of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It is an introduction to the Learning Registry services.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References

- :doc:`Resource Distribution Network Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Resource Data Data Models <../Resource_Data_Data_Model/index>`

- :doc:`Identity, Trust, Authentication, Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Data Model and API Attributes and Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

Different types of services are detailed independently.

- :doc:`Distribution <../Distribution_Services/index>`

- :doc:`Publish <../Publish_Services/index>`

- :doc:`Access <../Access_Services/index>`

- :doc:`Broker <../Broker_Services/index>`

- :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`



-----------------
Services and APIs
-----------------

The services and their APIs provide the functionality that edge node producer and consumer agents use to push resource data into the distribution network and to discover and pull resource data from the network.
They also define how to distribute the resource data throughout a network and how to manage, discover and observe resource distribution network behavior.

The specification defined types of services follows.
Any non gateway node MAY provide any of these services.
A node MAY provide additional services not specified herein.


- :doc:`Distribution <../Distribution_Services/index>`

  - :ref:`Resource Data Distribution Service <Resource Data Distribution Service>`

- :doc:`Publish <../Publish_Services/index>`

  - :ref:`Basic Publish Service`

  - :ref:`Basic Delete Service`

- :doc:`Access <../Access_Services/index>`

  - :ref:`Basic Obtain Service`

  - :ref:`Basic Harvest Service`

  - :ref:`OAI-PMH Harvest Service`

- :doc:`Broker <../Broker_Services/index>` -- none currently defined

- :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

  - :ref:`Network Node Status Service`

  - :ref:`Network Node Description Service`

  - :ref:`Network Node Services Service`

  - :ref:`Resource Distribution Network Policy Service`

*NB*: There is no mechanism to reserve names for APIs, tag them as authoritative (i.e., they are defined in this specification), etc.
A future version of the specification MAY extend the service definition to include tags (e.g., authoritative, experimental, third-party) and other validation or conformance information.

Services and APIs are RESTful and bound to a particular node in the resource distribution network.
Service descriptions include the API call (HTTP binding), the API arguments, the message payload (using the JSON-like notation), the service results (using JSON-like notation), error codes, an informative pseudo code description of a *possible* implementation, and the network node service description data.

The :ref:`Network Node Service Description Data Model <Network Node Service Description Data Model>` provides a machine and human readable description of the service; an instance of the description document is stored at the node that provides the service.

Additional constraints on API attributes, HTTP bindings (headers, HTTP errors), error processing and behaviors are  described in the :doc:`Data Model and API Attributes and Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part of the specification.

Except as noted, services SHALL NOT be required to be provisioned at a node.
An implementation SHALL NOT assume the provision of any service at any node, i.e., the implementation of one service cannot rely upon another service.

▲Except as noted, services SHALL be fully independent; the implementation and provisioning of a service at a node SHALL NOT assume that any other service is deployed at the node.



----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                            |
+-------------+----------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document. `Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_                                            |
+-------------+----------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | 20110927 | DR         | Editorial updates to create stand alone version. Clarify non dependence of service deployment.Archived copy location TBD. (V SA 0.50.0)                                                                                               |
+-------------+----------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Archived copy location TBD. (V SA:x.xx.x)                                                                                                                                                                                             |
+-------------+----------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | This document extracted from Google Doc and converted to RestructuredText. `Archive copy (V SA:0.50.0) <https://docs.google.com/document/d/1RGRnuaQ9YFsWLExPnrQRGEgZT5fx000nGGo-PKeFLrY/edit>`_                                       |
+-------------+----------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+



----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
