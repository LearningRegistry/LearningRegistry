


======================================================================
Broker Services: Learning Registry Technical Specification V BS:0.50.1
======================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.

:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.

This document is part of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It describes one type of services and APIs deployable at nodes in a Learning Registry Distribution Network.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General <../General_Matter/index>` :doc:`Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References

- :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>`

- :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>`

- :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Other <../Services_and_APIs/index>` :doc:`Services <../Services_and_APIs/index>` including :doc:`Distribution <../Distribution_Services/index>`, :doc:`Publish <../Publish_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that specific criteria for the services and APIs are presented in the :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>` part, the :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>` part describes the data that broker services process, and the :doc:`Identity <../Identity_Trust_Auth_and_Security/index>`, :doc:`Trust <../Identity_Trust_Auth_and_Security/index>`, :doc:`Authentication <../Identity_Trust_Auth_and_Security/index>`, :doc:`Security <../Identity_Trust_Auth_and_Security/index>` part describes security requirements.

.. _Broker Services:

---------------
Broker Services
---------------

Broker services operate at a network node to process, transform, augment, amplify or otherwise manipulate the resource data held at a node.
No broker services are currently defined.
Broker services may be defined in future drafts or versions of the specification.



----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                                                                                   |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document. `Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_                                                                                                   |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | 20110926 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V BS:0.50.0)                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Archived copy location TBD. (V BS:x.xx.x)                                                                                                                                                                                                                                                    |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | This document extracted from the Google Doc and converted to RestructuredText. `Archive Copy (V BS:0.50.0) <https://docs.google.com/document/d/1-dasdKJ_gDW-YEi4S7-g8ODGOp5To9xfXR-qbZVwt-Q/edit>`_                                                                                          |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
