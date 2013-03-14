


=========================================================================
General Matter: Learning Registry Technical Specification - V GM:0.50.1
=========================================================================

.. include:: ../stability.txt

See the `Change Log`_ for links to prior stable versions.


:changes:`Shading indicates major changes and additions from the prior version (0.24.0). Also indicated with ▲.`

:deletions:`Significant deletions are shaded.`

:deprecation:`Features to be deprecated in a future version are shaded and indicated with ▼.`

This document is part of one or more versions of the :doc:`Learning Registry Technical Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.


This document is part of the  :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. This part provides general information, including: an introduction to the Learning Registry, Licenses, Notation, Glossary, References, etc.
Readers of the other parts of the Learning Registry Technical Specification should be aware of the contents of this part.





--------------------------
Learning Registry Overview
--------------------------

The Learning Registry [http://learningregistry.org/] aims to make “learning resources easier to **find**, easier to **access** and easier to **integrate** into learning environments *wherever* they are stored -- around the country and the world.” It defines a learning resource distribution network model and a set of open APIs and open interoperability standards to provide three fundamental, enabling capabilities:

1. a lightweight mechanism to publish (push) learning resources (or metadata or paradata describing the resources) into a learning resource distribution network, independent of format or data type (e.g., resource, metadata or paradata);

2. the ability for anyone to consume the published data and then, in turn, to publish additional feedback about the resources’ use into the network (e.g., additional paradata), amplifying the overall knowledge about the resources;

3. a high-latency, loosely connected network of master-master synchronizing brokers distributing resources, metadata and paradata.

There is no central control, central registries or central repositories in the core resource distribution network.
Published data can eventually flow to all nodes in the network.
The network aims to be self assembling.
Edge services can connect to any distribution node to find out what resources (and resource sources) are in the network, what’s changed, what’s being used, etc.
Organizations may build consumer-facing, value-added services at the edge nodes to enable using, finding, sharing, and amplifying the resources, metadata and paradata for user communities.
The Learning Registry provides *social* *networking* *for* *metadata* (trusted social collaboration around learning resources), enabling a *learning* *layer* on the social web.





---------------------
Specification License
---------------------

:deletions:`This specification is being developed under the Open Web Foundation Contributor License Agreement - Contributor Copyright Grant (CLA 0.9).
The intent is that the final specification will be released under the Open Web Foundation Agreement (OWFa 0.9).
Later versions may apply.`

:changes:`▲The Learning Registry Technical Specification is being developed under the Open Web Foundation Contributor License Agreement 1.0 - Patent and Copyright (CLA 1.0)..
The intent is that the final specification will be released under the Open Web Foundation Final Specification Agreement (OWFa 1.0).
Later versions may apply.`

        Your use of this Specification may be subject to other third party rights.
        THIS SPECIFICATION IS PROVIDED “AS IS.” The contributors expressly disclaim any warranties (express, implied, or otherwise), including implied warranties of merchantability, non-infringement, fitness for a particular purpose, or title, related to the Specification.
        The entire risk as to implementing or otherwise using the Specification is assumed by the Specification implementer and user.
        IN NO EVENT WILL ANY PARTY BE LIABLE TO ANY OTHER PARTY FOR LOST PROFITS OR ANY FORM OF INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES OF ANY CHARACTER FROM ANY CAUSES OF ACTION OF ANY KIND WITH RESPECT TO THIS SPECIFICATION OR ITS GOVERNING AGREEMENT, WHETHER BASED ON BREACH OF CONTRACT, TORT (INCLUDING NEGLIGENCE), OR OTHERWISE, AND WHETHER OR NOT THE OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.





--------
Notation
--------

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in the Learning Registry Technical Specification are to be interpreted as described in `RFC 2119 <http://tools.ietf.org/html/rfc2119>`_.

The vocabulary of terms used in describing the Learning Registry and in the Learning Registry Technical Specification are listed in the `Glossary`_.
Specific terms are set in **bold** when introduced in context.

Data models are described in a JSON-like notation.
It follows JSON syntax, but instead of providing the value for a name, the data model defines the JavaScript data type of the named element.
A description of the element, further restrictions on the value space (e.g., if a string is a URL) and if the element is optional or required is described in a comment.
This model is used for convenience in early prototyping.
A future version of the specification may describe the data models and their implementation binding independently.





-----------
Conformance
-----------

There is no overall conformance statement for the Learning Registry Technical Specification.
The Learning Registry Test Suite (link TBD) MAY be used to test an implementation.
However, passing the Test Suite does not imply conformance to this specification.
There is no defined “reference implementation” (by definition when there is a conflict between this specification and the reference implementation, the reference implementation is considered to be authoritative -- thus the lack of a reference implementation implies that the Learning Registry Technical Specification is authoratitive).

All pseudo code is informative; it is not a normative implementation design.
Behaviors defined in pseudo code are normative requirements on an implementation.
Behaviors are usually defined in normative text.

An organization MAY place tighter requirements on an implementation than those stated, e.g., it MAY constrain a MAY, SHOULD or OPTIONAL clause to MUST, SHALL or REQUIRED.
It MAY NOT relax any constraint.





------------------------
Specification Versioning
------------------------

:changes:`▲The following section is new in this version of the part.
The remainder is not highlighted.`

Different components of the Learning Registry Technical Specification and any implementation are versioned.
Version numbers of different components may be updated independently and version numbers of one component are not correlated with version numbers of other components.

- Learning Registry Technical Specification Part Version Numbers

  - Each part of the Learning Registry Technical Specification has its own version number.
    

  - The version number of any part may change independently of any other part.

- Learning Registry Technical Specification Part Version Numbers

  - The whole of the Learning Registry Technical Specification has its own version number.
    

  - The version number of the whole may change independently of a change to any part of the specification.
    

  - A change in the version of a part SHALL result in a change to the version number of the whole.
    

  - The reader SHALL NOT interpret any similarity between the version number of the whole and a version number of the part to imply that the version of a specific part is included in a specific version of the whole.

- Data Model Schema Version Numbers

  - Each data model schema has its own version number

  - Different version numbers for a data model schema imply a difference in the data model.
    

  - The version number of the part of the specification where the data model is defined may change independently from the version number of the data model (the part may change without otherwise changing the data model schema).
    

  - A change in the data model version SHALL result in a change in the version number of the part of the specification where the data model is defined.

  - The reader SHALL NOT interpret any similarity between the version number of a data model and the version number of any component of the Learning Registry Technical Specification (whole, part, service) to imply a correlation between the data model and the other component.

- Service/API Version Numbers

  - Each service or API definition has its own version numbers

  - Different version numbers for a service or API definition imply a difference in the service (behavior, interfaces).

  - The version number of the part of the specification where the service or API is defined may change independently from the version number of the service or API (the part may change without otherwise changing the service or API).

  - A change in the service or API version SHALL result in a change in the version number of the part of the specification where the service or API is defined.

  - The reader SHALL NOT interpret any similarity between the version number of a service or API definition and the version number of any component of the Learning Registry Technical Specification (whole, part, service) to imply a correlation between the service or API and the other component.

- Service Implementation Version Number

  - Each service implementation has its own version number.

  - The reader SHALL NOT interpret any similarity between the version number of a service implementation and the version number of the service or API definition in the Learning Registry Technical Specification to imply that the service implements the specific version of the definition.

  - A service implementation SHALL include a mechanism to correlate the implementation version with a specific version number of the definition of the service or API.

- Learning Registry Deployment Version Number

  - A deployment of the Learning Registry MAY have its own version number.

  - A deployment of the Learning Registry includes any number of services, each of which has their own implementation version number.





--------------------------------
Technical Specification Overview
--------------------------------

The Learning Registry Technical Specification is split into several parts:

- **Network**: The description of the resource distribution network and its parts.
  A fixed multi-level structure of network parts is used to support distributing content and to provide policy-based security and operations.

- **Data** **Models**: The data models that are used to describe the network and learning resources data.
  Data models are document oriented.

- **Services** **and** **APIs**: The APIs used to publish and consume data and those used to operate the network.
  The APIs are designed to abstract the logical behaviors of the Learning Registry from any particular implementation tools.

- :changes:`▲ **General Requirements:** Common behaviors and attributes that apply to all data models and behaviors.`

- :changes:`▲ **Identity and Trust:** Models of trust, authentication, authorization, identity and security.
  These models are applied to all data models and operations.`

- **Operations**: Operational procedures that apply to any implementation.






Design Principles
=================

The learning registry design and technical specification is based on several key principles:

- **Decentralized**: There are no centralized registries or repositories or central data stores.
  Thus all core data is replicated across the network.

- **Redundant**: There is no single point of failure in the design (an implementation may have single points of failure).

- **Abstracted**: Abstraction is critical to layering capabilities, e.g., network content replication is content type agnostic.
  

- **Minimal**: Specify only what is required.
  Features that are community specific or can be layered on top of the core design are excluded from the specification although essential elements needed to support such modeling are included.

- **Generic**: Prefer approaches, models, standards, etc., that have wide uptake beyond just the learning technology and digital repository space.

- **Secure**: Security is by design, e.g., default values lock down an implementation and must be explicitly overridden even to do common operations.

- **Trusted**: Data and operations need to be authentic and trusted

- **Document** **Oriented**: The design is targeted at a document-oriented system for implementation using document-oriented databases.

- **RESTful**: APIs are RESTful, and use `CoolURIs <http://www.w3.org/TR/cooluris/>`_ to return different data representations.

- **Scalable**: The design needs to seamlessly scale and perform at scale.

- **Extensible and Enabling**: The design is meant to enable new capabilities.
  Unless explicitly restricted (usually to satisfy security requirements) anything in the design is extensible.

- **Web 2.0 Friendly**: The design is based on current, widely implemented Web 2.0 technologies.





--------
Glossary
--------

The following terms are used in this document as defined.

Additional terms may be provided in a future draft or version of the specification.

.. glossary::

        access (v)
            to obtain resource data from a network node by an agent that is external to a resource distribution network.

        broker (n)
            a server process that provides transformative or data amplification processing of resource data.

        community (n)
            see *network* *community*.

        common node (n)
            a network node in a resource distribution network that may provide any service to process resource data and that may connect to any other node in the same resource distribution network for the distribution of resource data within the resource distribution network.

        distribute (v)
            to copy or synchronize resource data from one network node to another.

        gateway node (n)
            a network node in a resource distribution network that provides an interconnection to a network node in a different resource distribution network (either in the same network community or in a different network community) for the distribution of resource data across the network boundary.

        harvest (v)
            to access a network node and obtain sets of resource data; the accessing agent is the harvestor; the network node is the harvestee.
            Harvest is typically based on timestamps used to identify new resource data held at the harvestee.

        identifier (n)
            the name (i.e., a label [e.g., a string] in an authoritative context) associated with a thing (anything that can be given an identifier).

        learning resource (n)
            any (digital) resource that is designed for, or has been used, in an educational context.

        metadata (n)
            formally authored and curated information describing a learning resource.
            Also denoted *first* *party* metadata.

        network (n)
            see *resource* *distribution* *network**.
            * A network need not correspond to a physical or logical network of computing devices.

        network community (n)
            a group of interconnected resource distribution networks.
        

        network node (n)
            a service end point in a resource distribution network that may provide services to process resource data and that may connect to any other nodes to distribute resource data.
            A network node need not correspond to a physical or logical computing device.

        node (n)
            see *network* *node*.

        paradata (n)
            information describing the contextual use of a learning resource.
            It includes informally authored information and data obtained directly through monitoring the use of a learning resource, its metadata or its paradata.
            Also denoted *second* *party* metadata.

        publish (v)
            to submit resource data to a network node from a source external to the node’s resource distribution network.

        pull (v)
            to distribute resource data from A to B, initiated by B.

        push (v)
            to distribute resource data from A to B, initiated by A.

        resource (n)
            see *learning* *resource*.

        resource data (n)
            any data that describes a learning resource, including, but not limited to metadata and paradata.

        resource distribution network (n)
            a group of interconnected network nodes that operate under an agreed set of policies.

        service (n)
            a process applied to resource data or system descriptive and operational data operating on a network node.





----------
References
----------

References below contain both normative and informative references.
Unless otherwise noted, this specification references specific versions of other normative standards.
More recent versions SHALL NOT be used.

Additional references may be provided in a future draft or version of the specification.

- CoolURIs 2008: *Cool URIs for the Semantic Web*, http://www.w3.org/TR/cooluris/

- DC 1.1: *Dublin Core Metadata Element Set*, Version 1.1, http://dublincore.org/documents/dces/

- Benecode, *Bittorent Protocol Specification 1.0*, http://wiki.theory.org/BitTorrentSpecification#bencoding

- ECMAScript: ECMAScript Language Specification, 5th Edition, December 2009, ECMA Standard 262, http://www.ecma-international.org/publications/standards/Ecma-262.htm

- FRBR: *Functional Requirements for Bibliographic Records*,  International Federation of Library Associations and Institutions, 1998, ISBN: 359811382X, http://www.ifla.org/VII/s13/frbr/frbr.pdf

- GPG: *GNU PrivacyHandbook*, http://www.gnupg.org/gph/en/manual.html

- HKP: *TheOpenPGPHTTPKeyserverProtocol (HKP)* draft-shaw-openpgp-hkp-00.txt http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00

- ISO 8601: *Data elements and interchange formats*  --  *Information interchange*  -- *Representation of dates and times*,  ISO 8601:2004, http://www.iso.org/iso/catalogue_detail?csnumber=40874

- IEEE LOM: *IEEE* *Standard* *for* *Learning* *Object* *Metadata*, IEEE Std 1484.12.1™-2002, IEEE Computer Society, September 2002.

- OAI-PMH: *The* *Open* *Archives* *Initiative* *Protocol* *for* *Metadata* *Harvesting*, V2.0, http://www.openarchives.org/OAI/openarchivesprotocol.html

- OAUTH: *OAUTH*, http://oauth.net/

- RFC 3880: *OpenPGP* *Messange* *Format*, http://tools.ietf.org/rfc/rfc4880.txt

- RFC 4122: *A Universally Unique Identifier (UUID) URN Namespace*, RFC 4122, http://www.ietf.org/rfc/rfc4122.txt

- RFC 4627: *The application/json Media Type for JavaScript Object Notation (JSON),* http://tools.ietf.org/html/rfc4627

- SHS, *Secure* *Hash* *Standard*, FIPS PUBS 180-3, http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf

- SRU: *Search/Retrieval via URL Specifications*, SRU Version 1.2 Specifications, The Library of Congress, August 2007, http://www.loc.gov/standards/sru/specs/

- SWORD: *SWORD AtomPub Provife V 1.3*, http://www.swordapp.org/docs/sword-profile-1.3.html

- Unicode: *The Unicode Consortium*. The Unicode Standard, Version 6.0.0*, http://www.unicode.org/versions/Unicode6.0.0/

- UTF-8: TBC (where in Unicode 6.0.0 doc?)





----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                            |
+-------------+----------+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document. `Archived copy (V 0.24.0) <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_                            |
+-------------+----------+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | 20110926 | DR         | Editorial updates to create stand alone version. Changed license from OWA CLA 0.9 to OWA CLA 1.0. Added section on versioning. Archived copy location TBD. (V GM:0.50.0)                                              |
+-------------+----------+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | XXXArchived copy location TBD. (V GM:x.xx.x)                                                                                                                                                                          |
+-------------+----------+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.1      | 20130312 | JK         | Converted spec source format to RestructuredText. `Archive copy (V GM:0.50.0) <https://docs.google.com/document/d/1B5DqiN2YhjPZ5qApWGvWVyeuOjFpIOHiRlF9kjgPjzU/edit>`_                                                |
+-------------+----------+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+





----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
