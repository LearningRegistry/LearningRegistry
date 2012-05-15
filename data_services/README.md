# Data Services

## What does a Data Service Do?

A data service is a design pattern within Learning Registry that when followed, will allow you to leverage the _extract_ service to:

* Define custom logic to select resource data of interest. 
* Request resource data to get:

> * Resource Locator by Discriminator
> * Resource Locator by start of Discriminator
> * Resource Locator by Timestamp
> * Discriminator by Resource Locator
> * Discriminator by start of Resource Locator
> * Discriminator by Timestamp
> * Discriminated Resource Locator by Timestamp
> * All Discriminated Resources

The Prototype implementation is designed to use the _extract_ service to retrieve Resource Data that contains **Alignment to Standards** resource data. In this prototype, we are using the following criteria to determine if a Resource Data Description Document contains _Alignment to Standards_ data:

> * The resource_data is inline 
> * If the resource_data contains XML using the Dublin Core Terms (dct) schema, http://purl.org/dc/terms/, to extract `<dct:conformsTo>` elements that match one of the patterns within `ASNPatterns`.
> * If the resource_data contains JSON using the _LR Paradata 1.0_ specification, when the Paradata's `activity.verb.action` is `"matched"` or `"aligned"` and a `activity.related[n].id` matches one of the patterns within the `ASNPatterns`.

`ASNPatterns` is currently defined within _./standards-alignment/lib/alignment.js_ as:

> >        var ASNPatterns = [
> >            /https?:\/\/purl\.org\/ASN\/resources\/[A-Z0-9]+/g,        // legacy Jes&Co Achievement Standards Network (ASN) ID
> >            /https?:\/\/asn\.jesandco\.org\/resources\/[A-Z0-9]+/g     // new Jes&Co Achievement Standards Network (ASN) ID
> >        ];

The **Alignment to Standards** prototype implementation cat provide a Data Service that will allow use of the _extract_ service to request resource data and aggregations where ASN's are Discriminators, `resource_locator`'s are Resource resource_locator, and `node_timestamp`'s are Timestamps, which will enable us to get:

> * `resource_locator` by ASN
> * `resource_locator` by start of ASN
> * `resource_locator` by `node_timestamp`
> * ASN by `resource_locator`
> * ASN by start of `resource_locator`
> * ASN by `node_timestamp`
> * ASN `resource_locator`s by `node_timestamp`
> * All ASN `resource_locator`s

Timestamps SHALL be a long integer value representing seconds since epoch from UTC+0 timezone.

## Design Pattern

For the following, we will define as example data:

>     Resource Locator : "http://www.example.com/educational/resource" (`resource_locator`)
>     Discriminator    : "http://purl.com/ASN/resources/S000000" (ASN)
>     Timestamp        : 1330552901 (`node_timestamp` is "2012-02-29T22:01:32Z")

You will need to define MapReduce views in CouchDB the emit keys in the following convention:

        "discriminator-by-resource"    : [ Resource Locator, Discriminator ]
        "discriminator-by-resource-ts" : [ Resource Locator, Timestamp, Discriminator ]
        "resource-by-discriminator"    : [ Discriminator, Resource Locator ]
        "resource-by-discriminator-ts" : [ Discriminator, Timestamp, Resource Locator ]
        "resource-by-ts"               : [ Timestamp, Resource Locator ]
        "discriminator-by-ts"          : [ Timestamp, Discriminator ]

Each view should **not** implement a reduce function.

Using example data:

        "discriminator-by-resource"    : key=[ "http://www.example.com/educational/resource", "http://purl.com/ASN/resources/S000000" ] 
        "discriminator-by-resource-ts" : key=[ "http://www.example.com/educational/resource", 1330552901, "http://purl.com/ASN/resources/S000000" ] 
        "resource-by-discriminator"    : key=[ "http://purl.com/ASN/resources/S000000", "http://www.example.com/educational/resource" ] 
        "resource-by-discriminator-ts" : key=[ "http://purl.com/ASN/resources/S000000", 1330552901, "http://www.example.com/educational/resource" ] 
        "resource-by-ts"               : key=[ 1330552901, "http://www.example.com/educational/resource" ]
        "discriminator-by-ts"          : key=[ 1330552901, "http://purl.com/ASN/resources/S000000" ]

Definition of CouchDB keys in this manner will allow one to query CouchDB in the following manner:

* To get "All ASNs by Resource Locator":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/discriminator-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>",{}]'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/discriminator-by-resource?resource=<resource_locator>'



* To get "All ASNs by Resource Locator from Timestamp1 to until Timestamp2":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/discriminator-by-resource-ts?startkey=["<resource_locator>",<timestamp1>]&endkey=["<resource_locator>",<timestamp2>,{}]'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/discriminator-by-resource-ts?resource=<resource_locator>&from=<ISO8601timestamp1>&until=<ISO8601timestamp2>'




* To get "All ASNs by Resource Locator prefix":

  - CouchDB API: 

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/discriminator-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>\uD7AF"]&reduce=true&group_level=2'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/discriminator-by-resource?resource-starts-with=<resource_locator>'




* To get "All Resource Locators by ASN":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/resource-by-discriminator?startkey=["<asn>"]&endkey=["<asn>",{}]'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/resource-by-discriminator?discriminator=<asn>'




* To get "All Resource Locators by ASN from Timestamp1 to until Timestamp2":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/resource-by-discriminator-ts?startkey=["<asn>",<timestamp1>]&endkey=["<asn>",<timestamp2>,null]'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/resource-by-discriminator-ts?discriminator=<asn>&from=<ISO8601timestamp1>&until=<ISO8601timestamp2>'




* To get "All Resource Locators by ASN prefix":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/resource-by-discriminator?startkey=["<asn>"]&endkey=["<asn>\uD7AF"]'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/resource-by-discriminator?discriminator-starts-with=<asn>'




* To get "All ASN Resource Locators":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/discriminator-by-resource'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/discriminator-by-resource'




* To get "All ASN Resource Locators from Timestamp1 to until Timestamp2":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/resource-by-ts?startkey=[<timestamp1>]&endkey=[<timestamp2>,{}]'

  - Extract API:

>      curl -g -X GET 'http://<node address>/extract/standards-alignment/resource-by-ts?from=<ISO8601timestamp1>&until=<ISO8601timestamp2>'




* To get "All ASNs":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/resource-by-discriminator'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/resource-by-discriminator'




* To get "All ASNs from Timestamp1 to until Timestamp2":

  - CouchDB API:

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_list/to-json/discriminator-by-ts?startkey=[<timestamp1>]&endkey=[<timestamp2>,{}]'

  - Extract API:

>       curl -g -X GET 'http://<node address>/extract/standards-alignment/discriminator-by-ts?from=<ISO8601timestamp1>&until=<ISO8601timestamp2>'




## TODO / Notes

* Indentification of data service design documents.

> Add a extra map field onto the root of the design doc named `dataservices` that contains extended information about the data service (name, description, spec, etc.) See dataservices.json in standards-alignment design document, and in the data-services design document, the view named `list`, which might be used to discover data services.

* Convention driven design.

> We've identified a range of supported queries that would be supported in a generic fashion through the presence of specific views; it would make sense that a custom node may only need a limited set, so they should be able to reduce the number of views implemented, and the service api calling the views should detect what type of views are present, and only allow the subset queries.

* Why aren't there 'prefix' queries by date?

> These can't be done with a CouchDB view only, and the date filtering functionality would need to be encapsulated in a _list_ function.  See _How to deal with list functions_ above regarding advanced stuff.  To do this is possible, but just throws a wrench into complexity - this is supposed to be a K.I.S.S. solution towards extraction, follow the recipies and stuff should just work with batteries included.

* Why 'prefix' queries instead of regex?

> CouchDB views don't support regex.  You'd have to do the regex pattern match within a list function, which would eliminate the efficiency of the b-tree index.  So this falls into one of those advanced list function use cases.  It could be done, but to make it work more efficiently, you'd have to combine the regex with a range query so you're not iterating over the entire list. Based upon the type of things we heard the community ask for; all YouTube aligned resources, a sub-set of some site based upon URL paths; we think 'prefixes' work relatively well.

* What's with the wierd UTF-8 character in the 'prefix' query endkey?

> CouchDB follows UCS collation rules for UTF-8 strings, and different ranges within the 0x0 - 0xFFFF char code range that is _somewhat_ fully supported in Spidermonkey makes the last character in the collation sequence `\uD7AF`.  Since it's non-printable, it should be okay to be non-inclusive. See this Gist: https://gist.github.com/1904807 if you want to understand this better.


## Possible OUTPUT

        {
                "documents":[
                
                        {
                                "result_data": {
                                        /* 
                                                MapReduce aggregation formatted, could be in a paradata 'assertion' 
                                        */
                                },
                                "supplemental_data" : {

                                },
                                "resource_data": [
                                        /* doc ids of full docs */
                                ]

                        },
                        {
                                "result_data": {
                                        /* paradata */
                                },
                                "supplemental_data" : {

                                },
                                "resource_data": [
                                        /* doc ids of full docs */
                                ]

                        },
                        {
                                "result_data": {
                                        /* paradata */
                                },
                                "supplemental_data" : {

                                },
                                "resource_data": [
                                        /* doc ids of full docs */
                                ]

                        }

                ]
        }




