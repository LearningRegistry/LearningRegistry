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
        "all-resources"                : [ Timestamp, Resource Locator ]
        "all-discriminators"           : [ Timestamp, Discriminator ]

Each view **must** implement a `reduce` function.

Using example data:

        "discriminator-by-resource"    : key=[ "http://www.example.com/educational/resource", "http://purl.com/ASN/resources/S000000" ] 
        "discriminator-by-resource-ts" : key=[ "http://www.example.com/educational/resource", 1330552901, "http://purl.com/ASN/resources/S000000" ] 
        "resource-by-discriminator"    : key=[ "http://purl.com/ASN/resources/S000000", "http://www.example.com/educational/resource" ] 
        "resource-by-discriminator-ts" : key=[ "http://purl.com/ASN/resources/S000000", 1330552901, "http://www.example.com/educational/resource" ] 
        "all-resources"                : key=[ 1330552901, "http://www.example.com/educational/resource" ]
        "all-discriminators"           : key=[ 1330552901, "http://purl.com/ASN/resources/S000000" ]

Definition of CouchDB keys in this manner will allow one to query CouchDB in the following manner:

* To get "All ASNs by Resource Locator":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/discriminator-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>\uD7AF"]&reduce=true&group_level=2'

* To get "All ASNs by Resource Locator from Timestamp1 to until Timestamp2":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/discriminator-by-resource-ts?startkey=["<resource_locator>",<timestamp1>]&endkey=["<resource_locator>",<timestamp2>,null]&reduce=true&group_level=2'

* To get "All ASNs by Resource Locator prefix":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/discriminator-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>\uD7AF"]&reduce=true&group_level=2'

* To get "All Resource Locators by ASN":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/resource-by-discriminator?startkey=["<asn>"]&endkey=["<asn>\uD7AF"]&reduce=true&group_level=2'

* To get "All Resource Locators by ASN from Timestamp1 to until Timestamp2":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/resource-by-discriminator-ts?startkey=["<asn>",<timestamp1>]&endkey=["<asn>",<timestamp2>,null]&reduce=true&group_level=2'

* To get "All Resource Locators by ASN prefix":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/key-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>\uD7AF"]&reduce=true&group_level=2'

* To get "All ASN Resource Locators":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/key-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>\uD7AF"]&reduce=true&group_level=2'

* To get "All ASN Resource Locators from Timestamp1 to until Timestamp2":

>       curl -g -X GET 'http://<couchdb>/resource_data/_design/standards-alignment/_view/key-by-resource?startkey=["<resource_locator>"]&endkey=["<resource_locator>\uD7AF"]&reduce=true&group_level=2'
