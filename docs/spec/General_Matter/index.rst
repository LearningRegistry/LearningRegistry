
.. _h.u6sbhsuktqyj:

=========================================================================
General Matter: Learning Registry Technical Specification - V GM:0.50.0
=========================================================================

Draft in Progress.
See the :ref:`Change<h.vqkk28dmgzlf>` :ref:`Log<h.vqkk28dmgzlf>` for links to prior stable versions.


:changes:`Shading`:changes:` `:changes:`indicates`:changes:` `:changes:`major`:changes:` `:changes:`changes`:changes:` `:changes:`and`:changes:` `:changes:`additions`:changes:` `:changes:`from`:changes:` `:changes:`the`:changes:` `:changes:`prior`:changes:` `:changes:`version`:changes:` (0.24.0).
`:changes:`Also`:changes:` `:changes:`indicated`:changes:` `:changes:`with` ▲:changes:`.`

:deletions:`Significant`:deletions:` `:deletions:`deletions`:deletions:` `:deletions:`are`:deletions:` `:deletions:`shaded`:deletions:`.`

:deprecation:`Features`:deprecation:` `:deprecation:`to`:deprecation:` `:deprecation:`be`:deprecation:` `:deprecation:`deprecated`:deprecation:` `:deprecation:`in`:deprecation:` `:deprecation:`a`:deprecation:` `:deprecation:`future`:deprecation:` `:deprecation:`version`:deprecation:` `:deprecation:`are`:deprecation:` `:deprecation:`shaded`:deprecation:` `:deprecation:`and`:deprecation:` `:deprecation:`indicated`:deprecation:` `:deprecation:`with`▼:deprecation:`.`

This document is part of one or more versions of the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. It may contain links to other parts of the Specification.
These links may link to the most recent version of a part, not to the version of the part that corresponds to this version of this part.
Go to the appropriate version of the Specification that links to this version of this part, and follow the links there to the referenced part to find the version of the part that corresponds to this version of this part.

    :ref:`General<h.u6sbhsuktqyj>` :ref:`Matter<h.u6sbhsuktqyj>`:ref:`: <h.u6sbhsuktqyj>`:ref:`Learning<h.u6sbhsuktqyj>` :ref:`Registry<h.u6sbhsuktqyj>` :ref:`Technical<h.u6sbhsuktqyj>` :ref:`Specification<h.u6sbhsuktqyj>`:ref:` - <h.u6sbhsuktqyj>`:ref:`V<h.u6sbhsuktqyj>` :ref:`GM<h.u6sbhsuktqyj>`:ref:`:0.50.0<h.u6sbhsuktqyj>`

        :ref:`Learning<h.t8dv95qkagu4>` :ref:`Registry<h.t8dv95qkagu4>` :ref:`Overview<h.t8dv95qkagu4>`

        :ref:`Specification<h.bflimlt80rpq>` :ref:`License<h.bflimlt80rpq>`

        :ref:`Notation<h.cu2ipktikrsa>`

        :ref:`Conformance<h.whmj37vjr0jk>`

        :ref:`Specification<h.lisx85v54wl>` :ref:`Versioning<h.lisx85v54wl>`

        :ref:`Technical<h.o12ejzxfggen>` :ref:`Specification<h.o12ejzxfggen>` :ref:`Overview<h.o12ejzxfggen>`

            :ref:`Design<h.9vpjmlmi28mv>` :ref:`Principles<h.9vpjmlmi28mv>`

        :ref:`Glossary<h.8n9oub9badbo>`

        :ref:`References<h.76rvgj-gh9lot>`

        :ref:`Change<h.vqkk28dmgzlf>` :ref:`Log<h.vqkk28dmgzlf>`

        :ref:`Working<h.tph0s9vmrwxu>` :ref:`Notes<h.tph0s9vmrwxu>` :ref:`and<h.tph0s9vmrwxu>` :ref:`Placeholder<h.tph0s9vmrwxu>` :ref:`Text<h.tph0s9vmrwxu>`

This document is part of the  :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>`. This part provides general information, including: an introduction to the Learning Registry, Licenses, Notation, Glossary, References, etc.
Readers of the other parts of the Learning Registry Technical Specification should be aware of the contents of this part.



.. _h.t8dv95qkagu4:

--------------------------
Learning Registry Overview
--------------------------

The Learning Registry [`http <http://www.google.com/url?q=http%3A%2F%2Flearningregistry.org%2F&sa=D&sntz=1&usg=AFQjCNH0Q7yFYPqAD-Zg9qiJ8rq8DVYYKg>`_://`learningregistry <http://www.google.com/url?q=http%3A%2F%2Flearningregistry.org%2F&sa=D&sntz=1&usg=AFQjCNH0Q7yFYPqAD-Zg9qiJ8rq8DVYYKg>`_.`org <http://www.google.com/url?q=http%3A%2F%2Flearningregistry.org%2F&sa=D&sntz=1&usg=AFQjCNH0Q7yFYPqAD-Zg9qiJ8rq8DVYYKg>`_/] aims to make “learning resources easier to **find**, easier to **access** and easier to **integrate** into learning environments *wherever* they are stored -- around the country and the world.” It defines a learning resource distribution network model and a set of open APIs and open interoperability standards to provide three fundamental, enabling capabilities:

1. a lightweight mechanism to publish (push) learning resources (or metadata or paradata describing the resources) into a learning resource distribution network, independent of format or data type (e.g., resource, metadata or paradata);

2. the ability for anyone to consume the published data and then, in turn, to publish additional feedback about the resources’ use into the network (e.g., additional paradata), amplifying the overall knowledge about the resources;

3. a high-latency, loosely connected network of master-master synchronizing brokers distributing resources, metadata and paradata.

There is no central control, central registries or central repositories in the core resource distribution network.
Published data can eventually flow to all nodes in the network.
The network aims to be self assembling.
Edge services can connect to any distribution node to find out what resources (and resource sources) are in the network, what’s changed, what’s being used, etc.
Organizations may build consumer-facing, value-added services at the edge nodes to enable using, finding, sharing, and amplifying the resources, metadata and paradata for user communities.
The Learning Registry provides *social* *networking* *for* *metadata* (trusted social collaboration around learning resources), enabling a *learning* *layer* on the social web.



.. _h.bflimlt80rpq:

---------------------
Specification License
---------------------

:deletions:`This`:deletions:` `:deletions:`specification`:deletions:` `:deletions:`is`:deletions:` `:deletions:`being`:deletions:` `:deletions:`developed`:deletions:` `:deletions:`under`:deletions:` `:deletions:`the`:deletions:` `:deletions:`Open`:deletions:` `:deletions:`Web`:deletions:` `:deletions:`Foundation`:deletions:` `:deletions:`Contributor`:deletions:` `:deletions:`License`:deletions:` `:deletions:`Agreement`:deletions:` - `:deletions:`Contributor`:deletions:` `:deletions:`Copyright`:deletions:` `:deletions:`Grant`:deletions:` (`:deletions:`CLA`:deletions:` 0.9`:deletions:`).
`:deletions:`The`:deletions:` `:deletions:`intent`:deletions:` `:deletions:`is`:deletions:` `:deletions:`that`:deletions:` `:deletions:`the`:deletions:` `:deletions:`final`:deletions:` `:deletions:`specification`:deletions:` `:deletions:`will`:deletions:` `:deletions:`be`:deletions:` `:deletions:`released`:deletions:` `:deletions:`under`:deletions:` `:deletions:`the`:deletions:` `:deletions:`Open`:deletions:` `:deletions:`Web`:deletions:` `:deletions:`Foundation`:deletions:` `:deletions:`Agreement`:deletions:` (`:deletions:`OWFa`:deletions:` 0.9`:deletions:`).
`:deletions:`Later`:deletions:` `:deletions:`versions`:deletions:` `:deletions:`may`:deletions:` `:deletions:`apply`:deletions:`.`

▲:changes:`The`:changes:` `:changes:`Learning`:changes:` `:changes:`Registry`:changes:` `:changes:`Technical`:changes:` `:changes:`Specification`:changes:` `:changes:`is`:changes:` `:changes:`being`:changes:` `:changes:`developed`:changes:` `:changes:`under`:changes:` `:changes:`the`:changes:` `:changes:`Open`:changes:` `:changes:`Web`:changes:` `:changes:`Foundation`:changes:` `:changes:`Contributor`:changes:` `:changes:`License`:changes:` `:changes:`Agreement`:changes:` 1.0 - `:changes:`Patent`:changes:` `:changes:`and`:changes:` `:changes:`Copyright`:changes:` (`:changes:`CLA`:changes:` 1.0).`:changes:`.
`:changes:`The`:changes:` `:changes:`intent`:changes:` `:changes:`is`:changes:` `:changes:`that`:changes:` `:changes:`the`:changes:` `:changes:`final`:changes:` `:changes:`specification`:changes:` `:changes:`will`:changes:` `:changes:`be`:changes:` `:changes:`released`:changes:` `:changes:`under`:changes:` `:changes:`the`:changes:` `:changes:`Open`:changes:` `:changes:`Web`:changes:` `:changes:`Foundation`:changes:` `:changes:`Final`:changes:` `:changes:`Specification`:changes:` `:changes:`Agreement`:changes:` (`:changes:`OWFa`:changes:` `:changes:`1.0)`:changes:`.
`:changes:`Later`:changes:` `:changes:`versions`:changes:` `:changes:`may`:changes:` `:changes:`apply`:changes:`.`

        Your use of this Specification may be subject to other third party rights.
        THIS SPECIFICATION IS PROVIDED “AS IS.” The contributors expressly disclaim any warranties (express, implied, or otherwise), including implied warranties of merchantability, non-infringement, fitness for a particular purpose, or title, related to the Specification.
        The entire risk as to implementing or otherwise using the Specification is assumed by the Specification implementer and user.
        IN NO EVENT WILL ANY PARTY BE LIABLE TO ANY OTHER PARTY FOR LOST PROFITS OR ANY FORM OF INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES OF ANY CHARACTER FROM ANY CAUSES OF ACTION OF ANY KIND WITH RESPECT TO THIS SPECIFICATION OR ITS GOVERNING AGREEMENT, WHETHER BASED ON BREACH OF CONTRACT, TORT (INCLUDING NEGLIGENCE), OR OTHERWISE, AND WHETHER OR NOT THE OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



.. _h.cu2ipktikrsa:

--------
Notation
--------

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in the Learning Registry Technical Specification are to be interpreted as described in `RFC <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Fhtml%2Frfc2119&sa=D&sntz=1&usg=AFQjCNEifotriMBsHSbNZlbtV_IVSzvraQ>`_` 2119 <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Fhtml%2Frfc2119&sa=D&sntz=1&usg=AFQjCNEifotriMBsHSbNZlbtV_IVSzvraQ>`_.

The vocabulary of terms used in describing the Learning Registry and in the Learning Registry Technical Specification are listed in the :ref:`Glossary<h.8n9oub9badbo>`.
Specific terms are set in **bold** when introduced in context.

Data models are described in a JSON-like notation.
It follows JSON syntax, but instead of providing the value for a name, the data model defines the JavaScript data type of the named element.
A description of the element, further restrictions on the value space (e.g., if a string is a URL) and if the element is optional or required is described in a comment.
This model is used for convenience in early prototyping.
A future version of the specification may describe the data models and their implementation binding independently.



.. _h.whmj37vjr0jk:

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



.. _h.lisx85v54wl:

------------------------
Specification Versioning
------------------------

▲:changes:`The`:changes:` `:changes:`following`:changes:` `:changes:`section`:changes:` `:changes:`is`:changes:` `:changes:`new`:changes:` `:changes:`in`:changes:` `:changes:`this`:changes:` `:changes:`version`:changes:` `:changes:`of`:changes:` `:changes:`the`:changes:` `:changes:`part`:changes:`.
`:changes:`The`:changes:` `:changes:`remainder`:changes:` `:changes:`is`:changes:` `:changes:`not`:changes:` `:changes:`highlighted`:changes:`.`

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



.. _h.o12ejzxfggen:

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

- ▲:changes:`**General**`:changes:` `:changes:`**Requirements**`:changes:`: `:changes:`Common`:changes:` `:changes:`behaviors`:changes:` `:changes:`and`:changes:` `:changes:`attributes`:changes:` `:changes:`that`:changes:` `:changes:`apply`:changes:` `:changes:`to`:changes:` `:changes:`all`:changes:` `:changes:`data`:changes:` `:changes:`models`:changes:` `:changes:`and`:changes:` `:changes:`behaviors`:changes:`.`

- ▲:changes:`**Identity**`:changes:` `:changes:`**and**`:changes:` `:changes:`**Trust**`:changes:`**:**`:changes:` `:changes:`Models`:changes:` `:changes:`of`:changes:` `:changes:`trust`:changes:`, `:changes:`authentication`:changes:`, `:changes:`authorization`:changes:`, `:changes:`identity`:changes:` `:changes:`and`:changes:` `:changes:`security`:changes:`.
  `:changes:`These`:changes:` `:changes:`models`:changes:` `:changes:`are`:changes:` `:changes:`applied`:changes:` `:changes:`to`:changes:` `:changes:`all`:changes:` `:changes:`data`:changes:` `:changes:`models`:changes:` `:changes:`and`:changes:` `:changes:`operations`:changes:`.`

- **Operations**: Operational procedures that apply to any implementation.



.. _h.9vpjmlmi28mv:

-----------------
Design Principles
-----------------

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

- **RESTful**: APIs are RESTful, and use `CoolURIs <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_ to return different data representations.

- **Scalable**: The design needs to seamlessly scale and perform at scale.

- **Extensible** **and** **Enabling**: The design is meant to enable new capabilities.
  Unless explicitly restricted (usually to satisfy security requirements) anything in the design is extensible.

- **Web**** 2.0 ****Friendly**: The design is based on current, widely implemented Web 2.0 technologies.



.. _h.8n9oub9badbo:

--------
Glossary
--------

The following terms are used in this document as defined.

Additional terms may be provided in a future draft or version of the specification.

        *access* (v)*: * to obtain resource data from a network node by an agent that is external to a resource distribution network.

        *broker* (n): a server process that provides transformative or data amplification processing of resource data.

        *community* (n): see *network* *community*.

        *common* *node* (n): a network node in a resource distribution network that may provide any service to process resource data and that may connect to any other node in the same resource distribution network for the distribution of resource data within the resource distribution network.

        *distribute* (v): to copy or synchronize resource data from one network node to another.

        *gateway* *node* (n): a network node in a resource distribution network that provides an interconnection to a network node in a different resource distribution network (either in the same network community or in a different network community) for the distribution of resource data across the network boundary.

        *harvest* (v): to access a network node and obtain sets of resource data; the accessing agent is the harvestor; the network node is the harvestee.
        Harvest is typically based on timestamps used to identify new resource data held at the harvestee.

        *identifier* (n): the name (i.e., a label [e.g., a string] in an authoritative context) associated with a thing (anything that can be given an identifier).

        *learning* *resource* (n): any (digital) resource that is designed for, or has been used, in an educational context.

        *metadata* (n): formally authored and curated information describing a learning resource.
        Also denoted *first* *party* metadata.

        *network* (n): see *resource* *distribution* *network**.
        * A network need not correspond to a physical or logical network of computing devices.

        *network* *community* (n): a group of interconnected resource distribution networks.
        

        *network* *node* (n): a service end point in a resource distribution network that may provide services to process resource data and that may connect to any other nodes to distribute resource data.
        A network node need not correspond to a physical or logical computing device.

        *node* (n): see *network* *node*.

        *paradata* (n): information describing the contextual use of a learning resource.
        It includes informally authored information and data obtained directly through monitoring the use of a learning resource, its metadata or its paradata.
        Also denoted *second* *party* metadata.

        *publish* (v): to submit resource data to a network node from a source external to the node’s resource distribution network.

        *pull* (v): to distribute resource data from A to B, initiated by B.

        *push* (v): to distribute resource data from A to B, initiated by A.

        *resource* (n): see *learning* *resource**.*

        *resource* *data* (n): any data that describes a learning resource, including, but not limited to metadata and paradata.

        *resource* *distribution* *network* (n): a group of interconnected network nodes that operate under an agreed set of policies.

        *service* (n): a process applied to resource data or system descriptive and operational data operating on a network node.



.. _h.76rvgj-gh9lot:

----------
References
----------

References below contain both normative and informative references.
Unless otherwise noted, this specification references specific versions of other normative standards.
More recent versions SHALL NOT be used.

Additional references may be provided in a future draft or version of the specification.

- CoolURIs 2008: *Cool* *URIs* *for* *the* *Semantic* *Web*, `http <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_://`www <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_.`w <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_3.`org <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_/`TR <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_/`cooluris <http://www.google.com/url?q=http%3A%2F%2Fwww.w3.org%2FTR%2Fcooluris%2F&sa=D&sntz=1&usg=AFQjCNFF57WOpfu4EyZdRMGJKnodAVjexg>`_/

- DC 1.1: *Dublin* *Core* *Metadata* *Element* *Set*, Version 1.1, `http <http://dublincore.org/documents/dces/>`_://`dublincore <http://dublincore.org/documents/dces/>`_.`org <http://dublincore.org/documents/dces/>`_/`documents <http://dublincore.org/documents/dces/>`_/`dces <http://dublincore.org/documents/dces/>`_/

- Benecode, *Bittorent* *Protocol* *Specification** 1.0*, `http <http://wiki.theory.org/BitTorrentSpecification#bencoding>`_://`wiki <http://wiki.theory.org/BitTorrentSpecification#bencoding>`_.`theory <http://wiki.theory.org/BitTorrentSpecification#bencoding>`_.`org <http://wiki.theory.org/BitTorrentSpecification#bencoding>`_/`BitTorrentSpecification <http://wiki.theory.org/BitTorrentSpecification#bencoding>`_#`bencoding <http://wiki.theory.org/BitTorrentSpecification#bencoding>`_

- ECMAScript: ECMAScript Language Specification, 5th Edition, December 2009, ECMA Standard 262, `http <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_://`www <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_.`ecma <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_-`international <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_.`org <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_/`publications <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_/`standards <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_/`Ecma <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_-262.`htm <http://www.ecma-international.org/publications/standards/Ecma-262.htm>`_

- FRBR: *Functional* *Requirements* *for* *Bibliographic* *Records**,* International Federation of Library Associations and Institutions, 1998, ISBN: 359811382X, `http <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_://`www <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_.`ifla <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_.`org <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_/`VII <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_/`s <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_13/`frbr <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_/`frbr <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_.`pdf <http://www.ifla.org/VII/s13/frbr/frbr.pdf>`_

- GPG: *GNU* *Privacy* *Handbook*, `http <http://www.gnupg.org/gph/en/manual.html>`_://`www <http://www.gnupg.org/gph/en/manual.html>`_.`gnupg <http://www.gnupg.org/gph/en/manual.html>`_.`org <http://www.gnupg.org/gph/en/manual.html>`_/`gph <http://www.gnupg.org/gph/en/manual.html>`_/`en <http://www.gnupg.org/gph/en/manual.html>`_/`manual <http://www.gnupg.org/gph/en/manual.html>`_.`html <http://www.gnupg.org/gph/en/manual.html>`_

- HKP: *The* *OpenPGP* *HTTP* *Keyserver* *Protocol** (**HKP**)* draft-shaw-openpgp-hkp-00.txt `http <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_://`tools <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_.`ietf <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_.`org <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_/`html <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_/`draft <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_-`shaw <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_-`openpgp <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_-`hkp <http://tools.ietf.org/html/draft-shaw-openpgp-hkp-00>`_-00

- ISO 8601: *Data* *elements* *and* *interchange* *formats** -- **Information* *interchange** -- **Representation* *of* *dates* *and* *times**,* ISO 8601:2004, http://www.iso.org/iso/catalogue_detail?csnumber=40874

- IEEE LOM: *IEEE* *Standard* *for* *Learning* *Object* *Metadata*, IEEE Std 1484.12.1™-2002, IEEE Computer Society, September 2002.

- OAI-PMH: *The* *Open* *Archives* *Initiative* *Protocol* *for* *Metadata* *Harvesting*, V2.0, `http <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_://`www <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_.`openarchives <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_.`org <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_/`OAI <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_/`openarchivesprotocol <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_.`html <http://www.openarchives.org/OAI/openarchivesprotocol.html>`_

- OAUTH: *OAUTH*, `http <http://www.google.com/url?q=http%3A%2F%2Foauth.net%2F&sa=D&sntz=1&usg=AFQjCNEsWz0_k3G3issLX5KQo23b_xLQHA>`_://`oauth <http://www.google.com/url?q=http%3A%2F%2Foauth.net%2F&sa=D&sntz=1&usg=AFQjCNEsWz0_k3G3issLX5KQo23b_xLQHA>`_.`net <http://www.google.com/url?q=http%3A%2F%2Foauth.net%2F&sa=D&sntz=1&usg=AFQjCNEsWz0_k3G3issLX5KQo23b_xLQHA>`_/ 

- RFC 3880: *OpenPGP* *Messange* *Format**, *`http <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_://`tools <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_.`ietf <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_.`org <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_/`rfc <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_/`rfc <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_4880.`txt <http://www.google.com/url?q=http%3A%2F%2Ftools.ietf.org%2Frfc%2Frfc4880.txt&sa=D&sntz=1&usg=AFQjCNHmxOWQ8lg-tFMPALEIQDFGdV2ZHA>`_

- RFC 4122: *A* *Universally* *Unique* *Identifier** (**UUID**) **URN* *Namespace*, RFC 4122, `http <http://www.ietf.org/rfc/rfc4122.txt>`_://`www <http://www.ietf.org/rfc/rfc4122.txt>`_.`ietf <http://www.ietf.org/rfc/rfc4122.txt>`_.`org <http://www.ietf.org/rfc/rfc4122.txt>`_/`rfc <http://www.ietf.org/rfc/rfc4122.txt>`_/`rfc <http://www.ietf.org/rfc/rfc4122.txt>`_4122.`txt <http://www.ietf.org/rfc/rfc4122.txt>`_

- RFC 4627: *The* *application**/**json* *Media* *Type* *for* *JavaScript* *Object* *Notation** (**JSON**), *`http <http://tools.ietf.org/html/rfc4627>`_://`tools <http://tools.ietf.org/html/rfc4627>`_.`ietf <http://tools.ietf.org/html/rfc4627>`_.`org <http://tools.ietf.org/html/rfc4627>`_/`html <http://tools.ietf.org/html/rfc4627>`_/`rfc <http://tools.ietf.org/html/rfc4627>`_`4627 <http://tools.ietf.org/html/rfc4627>`_

- SHS, *Secure* *Hash* *Standard*, FIPS PUBS 180-3, `http <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_://`csrc <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_.`nist <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_.`gov <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_/`publications <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_/`fips <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_/`fips <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_180-3/`fips <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_180-3_`final <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_.`pdf <http://csrc.nist.gov/publications/fips/fips180-3/fips180-3_final.pdf>`_

- SRU: *Search**/**Retrieval* *via* *URL* *Specifications*, SRU Version 1.2 Specifications, The Library of Congress, August 2007, `http <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_://`www <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_.`loc <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_.`gov <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_/`standards <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_/`sru <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_/`specs <http://www.google.com/url?q=http%3A%2F%2Fwww.loc.gov%2Fstandards%2Fsru%2Fspecs%2F&sa=D&sntz=1&usg=AFQjCNFPhJ2d5J0c4yJlEhnLOXOcxTT63Q>`_/

- SWORD: *SWORD* *AtomPub* *Provife* *V** 1.3*, `http <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_://`www <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_.`swordapp <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_.`org <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_/`docs <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_/`sword <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_-`profile <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_-1.3.`html <http://www.google.com/url?q=http%3A%2F%2Fwww.swordapp.org%2Fdocs%2Fsword-profile-1.3.html&sa=D&sntz=1&usg=AFQjCNHHkJja-e1jcO4fC66PfWz750Gy5A>`_

- Unicode: *The* *Unicode* *Consortium**.
  **The* *Unicode* *Standard**, **Version** 6.0.0*, `http <http://www.google.com/url?q=http%3A%2F%2Fwww.unicode.org%2Fversions%2FUnicode6.0.0%2F&sa=D&sntz=1&usg=AFQjCNEA1ajNRmMGjqIGIqdNXH7OywKotQ>`_://`www <http://www.google.com/url?q=http%3A%2F%2Fwww.unicode.org%2Fversions%2FUnicode6.0.0%2F&sa=D&sntz=1&usg=AFQjCNEA1ajNRmMGjqIGIqdNXH7OywKotQ>`_.`unicode <http://www.google.com/url?q=http%3A%2F%2Fwww.unicode.org%2Fversions%2FUnicode6.0.0%2F&sa=D&sntz=1&usg=AFQjCNEA1ajNRmMGjqIGIqdNXH7OywKotQ>`_.`org <http://www.google.com/url?q=http%3A%2F%2Fwww.unicode.org%2Fversions%2FUnicode6.0.0%2F&sa=D&sntz=1&usg=AFQjCNEA1ajNRmMGjqIGIqdNXH7OywKotQ>`_/`versions <http://www.google.com/url?q=http%3A%2F%2Fwww.unicode.org%2Fversions%2FUnicode6.0.0%2F&sa=D&sntz=1&usg=AFQjCNEA1ajNRmMGjqIGIqdNXH7OywKotQ>`_/`Unicode <http://www.google.com/url?q=http%3A%2F%2Fwww.unicode.org%2Fversions%2FUnicode6.0.0%2F&sa=D&sntz=1&usg=AFQjCNEA1ajNRmMGjqIGIqdNXH7OywKotQ>`_6.0.0/

- UTF-8: TBC (where in Unicode 6.0.0 doc?)



.. _h.vqkk28dmgzlf:

----------
Change Log
----------

*NB*: The change log only lists major updates to the specification.


*NB*: Updates and edits may not results in a version update.

*NB*: See the :doc:`Learning <../Technical_Spec/index>` :doc:`Registry <../Technical_Spec/index>` :doc:`Technical <../Technical_Spec/index>` :doc:`Specification <../Technical_Spec/index>` for prior change history not listed below.

+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Version** | **Date** | **Author** | **Change**                                                                                                                                                                                                                                                                                   |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|             | 20110921 | DR         | This document extracted from the monolithic V 0.24.0 document.`Archived <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ `copy <https://docs.google.com/document/d/1Yi9QEBztGRzLrFNmFiphfIa5EF9pbV5B6i9Tk4XQEXs/edit?hl=en_US>`_ (V 0.24.0) |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 0.50.0      | 20110926 | DR         | Editorial updates to create stand alone version. Changed license from OWA CLA 0.9 to OWA CLA 1.0. Added section on versioning. Archived copy location TBD. (V GM:0.50.0)                                                                                                                     |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Future      | TBD      |            | XXXArchived copy location TBD. (V GM:x.xx.x)                                                                                                                                                                                                                                                 |
+-------------+----------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+



.. _h.tph0s9vmrwxu:

----------------------------------
Working Notes and Placeholder Text
----------------------------------

.. role:: deprecation

.. role:: deletions

.. role:: changes
