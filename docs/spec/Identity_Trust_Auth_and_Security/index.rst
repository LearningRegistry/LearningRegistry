


=========================================================================================
Identity, Trust, Auth and Security: Learning Registry Technical Specification V IT:0.50.1
=========================================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.

:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.

This document is part of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It describes a collection of issues related to identity, digital signature, authorization, authentication, trust, security and information assurance.

This document is not standalone.
The reader should be familiar with other parts of the specification, including, but not limited to:

- :doc:`General <../General_Matter/index>` :doc:`Matter <../General_Matter/index>`, including Licenses, Notation, Versioning, Glossary, References,

- :doc:`Resource <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Data <../Resource_Data_Data_Model/index>` :doc:`Models <../Resource_Data_Data_Model/index>`

- :doc:`Resource <../Resource_Distribution_Network_Model/index>` :doc:`Distribution <../Resource_Distribution_Network_Model/index>` :doc:`Network <../Resource_Distribution_Network_Model/index>` :doc:`Model <../Resource_Distribution_Network_Model/index>`

- :doc:`Data <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Model <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`API <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Attributes <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`and <../Data_Model_and_API_Attributes_and_Behaviors/index>` :doc:`Behaviors <../Data_Model_and_API_Attributes_and_Behaviors/index>`

- :doc:`Services <../Services_and_APIs/index>` including :doc:`Distribution <../Distribution_Services/index>`, :doc:`Publish <../Publish_Services/index>`, :doc:`Access <../Access_Services/index>`, :doc:`Broker <../Broker_Services/index>`, :doc:`Management <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Administration <../Mgmt_Admin_and_Discovery_Services/index>`/:doc:`Discovery <../Mgmt_Admin_and_Discovery_Services/index>`

- :doc:`Learning <../Operations/index>` :doc:`Registry <../Operations/index>` :doc:`Operations <../Operations/index>`

In particular, the reader needs to be aware that information from this part of the Technical Specification applies to all services.


.. _Identity and Digital Signatures:

-------------------------------
Identity and Digital Signatures
-------------------------------

Resource data description documents MAY be *signed* with a digital signatures.
The signing and identity approach insures there can be no impostors.
A persona (individual or organization) has a digital identity that can be used to sign a document.
Thus two resource data description documents signed by the same identity are both from the same persona (assuming the signer has protected their private data), and the signature is non repudiable.

A document’s digital signature provides the means to validate the authenticity of the signer’s identity and the integrity of the signed document.
The signature can only be used to verify that the signer controls their digital identify.
It does not indicate that the document can be trusted or that the signer’s digital identity maps to any real world identity.
Trust and reputation are not provided by identity or digital signatures, but are enabled by them.

Digital signing and validation of resource data description documents is an OPTIONAL feature of the specification.
A deployment of the Learning Registry MAY require documents be signed and validated.
If a resource data description document is to be signed and validated, the following procedures SHALL be used to sign the document and verify the signature.



Signing a Resource Data Description Document
--------------------------------------------

The controller of the identity (persona) that is used to sign the resource data description document MUST have a private/public PKI (public key infrastructure) key pair.
A deployment of the Learning Registry SHALL specify the digital signature scheme, i.e., how to generate PKI keys and the encryption/signing model, e.g., X.509, OpenPGP/RFC 4048 with 2048bit RSA certificates.
That method, along with the algorithm below SHALL be declared as the value of the signing_method key.

The controller of the identity MUST publish their public key at one or more locations where the key can be retrieved by an HTTP GET on the specified location.

The following process SHALL be used to generate the signature:

- Create the complete UTF-8 JSON form of the resource data description document.
  The JSON SHALL conform to the JSON definition in RFC4647. 

- Create a canonical document to sign:

  - Make a working copy of the JSON form of the resource data description document.
    

  - Eliminate all objects that are generated by a node in the Learning Registry network, leaving only those objects that are supplied by the user . Objects to be eliminated include: doc_id, publishing_node, update_timestamp, `▲node_timestamp,`:changes: create_timestamp

  - Eliminate all implementation-specific objects, i.e., in Couch these are the _* objects, e.g., _id, _rev (*NB*: These will exist only when verifying a signature.)

  - Eliminate all objects where the object is a number.
    (*NB*: There are currently no numeric objects.)

  - Eliminate the digital_signature object.

  - For a boolean object with value true, change the value to a string with the value "true".

  - For a boolean object with value false, change the value to a string with the value "false".

  - For an object with value null, change the value to a string with the value "null".

  - Encode the resulting JSON object using Bencode.
    The Bencoded output SHALL conform to the Bittorent Protocol Specification.

  - Hash the Bencoded output using SHA-256.

- Clear sign the hash using signer’s private key yielding the value for the signature.
  The signer (key owner) MAY be an identity that is just used to sign the document, or it MAY be the identity of the submitter.
  Other identities SHALL NOT be used to sign the document.

Insert the digital signature data into the complete, unmodified UTF-8 JSON form of the resource data description document.
Insert: 

- The signature value.

- The designation of one or more key_locations that can be used to obtain the public key of the signer.
  The value of a key_location designator SHALL be sufficient to obtain the public key by sending an HTTP GET request to the location (URL) value of the key_location.

- An optional value of the key_owner as the identity of the signer of the document if the submitter is not the signer.
  

- The value of signing_method SHALL be "LR-PGP.1.0".

*NB*: This specification does not indicate how to obtain keys, the signing method, when to sign documents or specify key locations.
A deployment of the Learning Registry that requires digital signatures SHALL indicate the approach used for generating and publishing keys and signing documents.

*NB*: Currently only signing of resource data description documents is specified.
A future version of the specification MAY require that other documents be signed.
The signing process SHALL be the same; the elements of the data model used in the signature vary by document type.



Validation the Signature of a Resource Data Description Document
----------------------------------------------------------------

Any node or data consumer MAY validate a signature to determine if the signing party did sign the resource data description document and to verify that the document has not been tampered with since being signed.

To validate the signature:

- Obtain the public key for the signer of the document.
  

  - Iterate through the list of key_locations in the order provided until you find an acceptable, usable public key.
    

    - Perform an HTTP GET on the location to get a document containing the public key.

    - Examine the returned document to obtain the public key.
      (*NB*: The returned document may include more than the key or the key may be embedded in the document.
      How to extract the key will depend on the type of certificate [e.g., doing a grep of the file for an ASCII-armored OpenPGP key].
      The type of certificate is goverened by the policies of the network and is not part of this specification.)

- Create a canonical document to verify.
  

  - Follow the exact procedure that was used to produce the hash of the document that was signed, e.g., eliminate fields, transform fields, encode, hash.

- Verify the signature value using the obtained public key.

Additional information on identity may be provided in a future version or draft of the specification.



--------------------------------
Authorization and Authentication
--------------------------------

Each service deployment at a node MAY specify authorization and authentication access controls and secure communications.
These three types of controls are defined independently.
Values for the controls are specified in the instance of the :ref:`Network Node Service Description Data Model <Network Node Service Description Data Model>` for the service.
Full details of how services implement these controls is not specified.



Authentication
--------------

A service MAY require authentication to access the service.
The service SHALL declare the authentication methods it supports.
The service MAY support multiple authentication methods.
Authentication methods are specified in the service_authz element of the service_auth element of the service description model.

The following authentication methods MAY be supported:

- None (none) -- the service is available without any authentication.
  If this authentication method is specified, other methods SHALL NOT be specified.

- Basic access authentication (basicauth) -- the service uses HTTP basic-auth for authentication.
  User identity and password credentials are included in the HTTP request.
  *NB*: A network node connectivity document includes the URL of the source and destination nodes used in content distribution, and a service description includes the URL of the service end point.
  For security, the URLs in these documents SHOULD NOT include credentials.
  

- OAUTH (oauth) -- the service is available through two-legged OAUTH.

- Secure Shell Protocol (SSH) -- the service is available through an SSH connection with SSH authentication.

*NB*: The list of authentication methods MAY be extended by a service.

Storage, processing and distribution of authentication credentials and establishing and provisioning OAUTH or SSH connections is out of scope for this specification.
A deployment of the Learning Registry SHALL specify how to provision authentication.



Authorization
-------------

A service MAY require authorization to access the service.
The service SHALL declare the authorization methods it supports.


Currently, only one authorization method is supported: a service MAY require an access key be included in the service request.
A service that requires an access key specifies that the value of the service_key element of the service_auth element of the service description model is TRUE.

A service that uses an access key authorization SHALL include the access key in the HTTP header of the service call.
What solution: Custom HTTP Header element, parameters, ...?

Storage, processing and distribution of access keys is out of scope for this specification.
A deployment of the Learning Registry SHALL specify how to provision access keys.



Network Communications Security
-------------------------------

A service MAY require that service HTTP requests be transmitted over a secure, encrypted communications channel.
The service SHALL declare the network security methods it supports.

Currently only one network security method is supported: a service MAY require use of HTTPS.
A service that requires a network security specifies that the value of the service_https element of the service_auth element of the service description model is TRUE.

Provisioning of HTTPS connections between clients and services is out of scope for this specification.
A deployment of the Learning Registry SHALL specify how to provision secure communications.



Network Ports
-------------

Sevices may be accessed on specific TCP/IP ports.
The service_endpoint element of a service description and the source_node_url and destination_node_url elements of the network node connectivity document SHALL include port numbers.

Additional information on authorization and authentication may be provided in a future version or draft of the specification.



-----
Trust
-----

The section on security and information assurance will be provided in a future version or draft of the specification.



----------------------------------
Security and Information Assurance
----------------------------------

The section on security and information assurance will be provided in a future version or draft of the specification.


All services SHOULD maintain a secure log of all service actions.
Details of logging requirements will be provided in a future version or draft of the specification.



----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                             |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document. `Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_             |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.49.0      | 20110927 | DR         | Editorial updates to create stand alone version.Archived copy location TBD. (V IT:0.49.0)                                                                                                              |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | TBD      | DR         | Renumber all document models and service documents.Archived copy location TBD. (V IT:0.50.0)                                                                                                           |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | Archived copy location TBD. (V IT:x.xx.x)                                                                                                                                                              |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | Converted specification source to RestructuredText. `Archived copy (V IT:0.49.0) <https://docs.google.com/document/d/1vK66RY4S6AVtMJXB7jSqwl30J6NVBj6Gs8UWBcP-IPY/edit>`_                              |
|             |          |            | node_timestamp removed from deprecation.                                                                                                                                                               |
+-------------+----------+------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
