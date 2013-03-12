


========================================================================
Services and APIs: Learning Registry Technical Specification V SA:0.50.0
========================================================================

Draft in Progress.

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

.. _h.d08onhltt4u1:

-----------------
Services and APIs
-----------------

The services and their APIs provide the functionality that edge node producer and consumer agents use to push resource data into the distribution network and to discover and pull resource data from the network.
They also define how to distribute the resource data throughout a network and how to manage, discover and observe resource distribution network behavior.

The specification defined types of services follows.
Any non gateway node MAY provide any of these services.
A node MAY provide additional services not specified herein.


- :doc:`Distribution <../Distribution_Services/index>`

  - `Resource Data Distribution Service <https://docs.google.com/a/learningregistry.org/document/d/1HW_JJBiWxNHoA5L1TuZrjWeK-DaFF0FTeMZBNIL5MqI/edit?hl=en_US#heading=h.vb0xt6mhzmg2>`_

- :doc:`Publish <../Publish_Services/index>`

  - `Basic Publish Service <https://docs.google.com/a/learningregistry.org/document/d/1kgTyRk1kIM3QvfU2JB1C9ARMuL7fCqsba7mOLQ3IKlw/edit?hl=en_US#heading=h.aera9k-4u6l42>`_

  - `Basic Delete Service <https://docs.google.com/a/learningregistry.org/document/d/1kgTyRk1kIM3QvfU2JB1C9ARMuL7fCqsba7mOLQ3IKlw/edit?hl=en_US#heading=h.rfe7ga-6sbjly>`_

- :doc:`Access <../Access_Services/index>`

  - `Basic Obtain Service <https://docs.google.com/a/learningregistry.org/document/d/1RRR7ZUjZRYgIyoIXPLsAZKluahqY7_Q7Gb00PHGHw8A/edit?hl=en_US#heading=h.23ll5s-2p4zua>`_

  - `Basic Harvest Service <https://docs.google.com/a/learningregistry.org/document/d/1RRR7ZUjZRYgIyoIXPLsAZKluahqY7_Q7Gb00PHGHw8A/edit?hl=en_US#heading=h.s3sst6-69kzq1>`_

  - `OAI-PMH Harvest Service <https://docs.google.com/a/learningregistry.org/document/d/1RRR7ZUjZRYgIyoIXPLsAZKluahqY7_Q7Gb00PHGHw8A/edit?hl=en_US#heading=h.art057-hbjxj4>`_

- :doc:`Broker <../Broker_Services/index>` -- none currently defined

- :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

  - `Network Node Status Service <https://docs.google.com/a/learningregistry.org/document/d/1lATgircOBUOmsoFwia8su2o--TZ88AG4GOmn5NQ6jAc/edit?hl=en_US#heading=h.x3qh8x-kqmikf>`_

  - `Network Node Description Service <https://docs.google.com/a/learningregistry.org/document/d/1lATgircOBUOmsoFwia8su2o--TZ88AG4GOmn5NQ6jAc/edit?hl=en_US#heading=h.ixbka3-k9h0vx>`_

  - `Network Node Services Service <https://docs.google.com/a/learningregistry.org/document/d/1lATgircOBUOmsoFwia8su2o--TZ88AG4GOmn5NQ6jAc/edit?hl=en_US#heading=h.5l0qus-ugg81l>`_

  - `Resource Distribution Network Policy Service <https://docs.google.com/a/learningregistry.org/document/d/1lATgircOBUOmsoFwia8su2o--TZ88AG4GOmn5NQ6jAc/edit?hl=en_US#heading=h.jlubtj-czhato>`_

*NB*: There is no mechanism to reserve names for APIs, tag them as authoritative (i.e., they are defined in this specification), etc.
A future version of the specification MAY extend the service definition to include tags (e.g., authoritative, experimental, third-party) and other validation or conformance information.

Services and APIs are RESTful and bound to a particular node in the resource distribution network.
Service descriptions include the API call (HTTP binding), the API arguments, the message payload (using the JSON-like notation), the service results (using JSON-like notation), error codes, an informative pseudo code description of a *possible* implementation, and the network node service description data.

The `Network Node Service Description Data Model <https://docs.google.com/a/learningregistry.org/document/d/1msnZC6RU9N72Omau0F4FNBO5YCU6hZrG1kKRs_z42Mc/edit?hl=en_US#heading=h.z0spjmvlcbb9>`_ provides a machine and human readable description of the service; an instance of the description document is stored at the node that provides the service.

Additional constraints on API attributes, HTTP bindings (headers, HTTP errors), error processing and behaviors are  described in the :doc:`Data Model and API Attributes and Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part of the specification.

Except as noted, services SHALL NOT be required to be provisioned at a node.
An implementation SHALL NOT assume the provision of any service at any node, i.e., the implementation of one service cannot rely upon another service.

▲Except as noted, services SHALL be fully independent; the implementation and provisioning of a service at a node SHALL NOT assume that any other service is deployed at the node.

.. _h.e1519o-y653zc:

----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                                                                                                                                                                                      |
+-------------+----------+------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document.`Archived <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ `copy <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ (`V <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ 0.24.0) |
+-------------+----------+------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | 20110927 | DR         | Editorial updates to create stand alone version. Clarify non dependence of service deployment.Archived copy location TBD. (V SA 0.50.0)                                                                                                                                                                                                                                                         |
+-------------+----------+------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Archived copy location TBD. (V SA:x.xx.x)                                                                                                                                                                                                                                                                                                                                                       |
+-------------+----------+------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. _h.tph0s9vmrwxu:

----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
