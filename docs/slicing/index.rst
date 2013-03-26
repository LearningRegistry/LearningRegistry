============================================
Learning Registry - Slicing
============================================

**Document Version: 1.0**

**Last Edited: September 14 , 2011**

Prepared by:

John Brecht, SRI International (john.brecht@sri.com)


.. figure:: images/cc-by-nc-sa.jpg
   :align: center
   :alt: Creative Commons Attribution NonCommercial ShareAlike 3.0 Unported License


Copyright 2011 - SRI International

This work is licensed under the `Creative Commons Attribution NonCommercial ShareAlike 3.0 Unported License. <http://creativecommons.org/licenses/by-nc-sa/3.0/>`_

------------
Introduction
------------

The Slice service provides a mechanism via which Learning Registry users
may retrieve a subset of Resource Description Data available at a given
node. Presently, the Slice service handles the following parameters:

-  **Date Range**: Matching against node\_timestamp, but at
   the granularity of a day

-  **Identity**: Matching any of the four possible identities:
   submitter, curator, owner, or signer

-  **Tags**: Matching any of a document's keys, schema type, or resource
   data type.


Any combination of either Date Range and Identity or Date Range or Tags may be passed to the Slice
services and are effectively ANDed together. That is, if a date range,
and tag are passed to Slice, resultant documents will have
been published: within that date range and has a key, schema type, or resource data
type matching that tag. Furthermore, multiple tags may be specified,
with the results being that the tags are ORed together. That is, if both
“mathematics” and “metadata” are specified in the list of tags,
documents will be returned that have either or both of those terms.
Thus, results have:

    date AND identity

OR

    date AND (tag1 OR tag2 OR tag3 ...)

Date range is specified with a start date (“from”) and end date
(“until”). Those dates and all dates in between are OR’d together as
follows:

    (from OR date2 OR date3 OR ... until) AND identity AND (tag1 OR tag2 OR tag3 ...)

If one specific date is wanted, then only start date (“from”) is
specified.

Again, any combination of the three parameters may be passed, so users
may Slice for:

    date

    identity

    tags

    date AND identity

    date AND tags


Future implementations MAY allow for multiple identities and for tags
to be ANDed.

~~~~~~~~~~~~~~~~~~~~~~
IDs vs. Full Documents
~~~~~~~~~~~~~~~~~~~~~~

The user may also specify a Boolean argument ‘ids\_only’. If true, only
doc IDs are returned, otherwise full Resource Data Description documents
are returned.

~~~~~~~~~~~~
Flow Control
~~~~~~~~~~~~

Some Learning Registry nodes will have Flow Control enabled for Slice.
This means that the node administrator can specify a cap on the number
of results returned for a given query. In such cases, when results are
returned, they will include a “resumption\_token” field. The value of
this field is a token that can be used as an argument to re-slice the
node, in which case, in which case the next page of results is returned.
(To set Flow Control parameters, node administrators should run
/config/services/Slice.py and they will be led through a series of
prompts to specify the values.)

-------
API
-------

.. http:get:: /slice

    :query from: *(date)* date of publication to learning registry in the form: YYYY-MM-DD, optional

    :query until: *(date)* date of publication to learning registry in the form: YYYY-MM-DD, optional

    :query identity: *(string)* the name of a person or organization that is the submitter, author, owner, or curator Case-insensitive, but full string match only, optional

    :query any_tags: *(list of string)* list of tags, matched against keys, payload\_schema, or resource\_data\_type. Case-insensitive, but full string match only, optional

    :query ids_only: *(boolean)* whether to return only a list of IDs or a list of full documents, optional, default is false

    :query resumption_token: *(string)* a token received from a previous query that instructs the node to return the next page of results for that query, optional


    **Example Usage**

    .. sourcecode:: http

        http://<nodeUrl>/slice?start_date=<date>&any_tags=<tag1>,<tag2>,<tag3>...

        http://<nodeUrl/slice?start_date=<date>&identity=<identity>


    **Response Object:**

    .. sourcecode:: http

        {
            “documents”: [                  // array of resource data description documents
                
                {
                
                    “doc\_ID”: “string”,    // ID of the document

                    "resource\_data\_description": {resource data description document} //complete document

                }

            ],

            "resumption\_token": "string",  // the token used to resume the next page of

                                            // results when flow control is used

            "resultCount": “integer”        // the total number of results for this set of

                                            // query parameters, regardless of flow control

        }

    OR, if ``ids_only`` is true:

    .. sourcecode:: http

        {
            “documents”: [                  // array of document IDs
                
                {
                
                    “doc\_ID”: “string”,    // ID of the document
                
                }

            ]

        }

-------------------------
Usage Examples
-------------------------

``http://<nodeUrl>/slice?any_tags=Arithmetic``

    Returns - documents containing “Arithmetic” as a key word

``http://<nodeUrl>/slice?any_tags=paradata&identity=CTE%20Online&full_docs=true``

    Returns - paradata documents submitted/owned/curated/signed by CTE Online, including full docs instead of just IDs

``http://<nodeUrl>/slice?from=2011-06-10``

    Returns - all Resource Data Descriptions submitted on June 10th, 2011

``http://<nodeUrl>/slice?any_tags=paradata&identity=CTE%20Online&from=2011-06-10&full\_docs=true``

    Returns - full docs of paradata submitted by CTE Online on June 10th, 2011

``http://<nodeUrl>/slice?any_tags=french,spanish,german``

    Returns - IDs of docs containing either ‘french’, ‘spanish’, or ‘german’ keywords.

``http://<nodeUrl>/slice?any_tags=french,spanish,german&resumption_token=eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJrZXlzIjogWyJtYXRoZW1hdGljcyJdLCAib2Zmc2V0IjogMTAwfQ.Zj05MgBHDJFrivmHjawnrV3EiFej_jllHOIEdiMnOoo``

    Returns - The next page of results for the above query, where the token specified came as part of the result object for a previous query

``http://<nodeUrl>/slice?from=2011-05-27&until=2011-06-14&any_tags=arithmetic``

    Returns - IDs of docs containing the keyword ‘arithmetic’ and were received by the Learning Registry between May 27th and June 14th 2011.

