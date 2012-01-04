# LR Jmeter Testing

The jmeter test suite is designed to provide a generic 
"smokescreen" test to quickly determine if a LR node is operational. It is functional 
and utilizes a black-box approach that allows the user to point the test at any url 
that corresponds to a Learning Registry node.

Currently, tests for each service description are the only implemented functional tests;
however, a library of utility functions has been created to easily create other black-box
functional tests should they become useful and/or necessary.

## Coverage

The tests cover each of the individual service descriptions available on a running node.
Each service description is extracted from the `/services` url, then compared against
a javascript object containing the expected values. The expected values in these ojbects
have been assigned according to each respective Network Node Service Description Data Model
found in version 0.24 of the LR Technical Specification. 

When appropriate, hard-coded values
are used as expected values and simple comparisons are made. For example, the `service_type`
property is part of a fixed vocabulary ("publish", "access", etc.) and thus a static assertion is made.

In cases where a value is required by the spec but can be dynamic (such as a timestamp), an
appropriate function is applied to assert that the value is indeed in the range of valid inputs.
Properties marked as optional in the specification are also accounted for, and are evaluated
only when returned from the server.

Optionally, an extra check can be made for extra keys not defined as part of the spec. This
assertion will raise an error if a key-value pair is returned from the server but not found
as part of the expected object. Since the Network Node Service Description Data Model is allowed
to have additional custom fields, this check is currently OFF by default.

The current commit also includes a separate test for the `/policy` data model that functions
in a manner identical to the aforementioned service description tests while testing for
the appropriate values for that service.

## Usage

The node to be targeted can be set using the LRNodeAddress and LRNodePort User-Defined Variables,
which means that running the test is very flexible with regard to environment. Because of its independence 
from the actual source code, unlike the python nosetests,
a user can decide whether to test a remote node or one found locally with minimal configuration changes.
That being said, it is also to be noted that these tests are NOT designed to be a replacement for the
nosetest unit tests, which provide a much more complete and robust way of testing an existing
Learning Registry installation.

This test was designed and developed using the GUI version of jmeter 2.6 on Windows. When finished,
the configurable pathnames were changed to work with a headless version of jmeter running on 
Ubuntu Server 10.01. Each functioned identically; however with the headless version, an output file
must be specified to view the passes/failures. The latter of the two configurations is what
can be found in this repo.

Please refer to the [jmeter project page](http://jmeter.apache.org) for more information on how
to properly install, configure, and run jmeter.

## Structure

### File Hierarchy

Inside this directory, you will find several subdirectories, each corresponding to a service that
Learning Registry nodes provide. Within each of these is another subdirectory corresponding to the
most recent known service version. This directory should contain all functional tests for that
version of the service. In the future, if a new version of the service is released, a new directory
should be created matching the new service version, and all applicable tests should be created
there based on the spec that the new service version implements.

The structure is purposefully designed so that each service can be tested on a node regardless of
the versions of the other services. To alter which version of each service you would like test,
modify the test plan, changing the "xVersion"-style User-Defined Variables to your desired version for each 
of the respective service(s).

### Test Files

Each test file (for example `svc_description.js`) should contain a javascript object that 
resembles a JSON document, which we will refer to as the **expected object**. Expected objects
should replicate the structure of the JSON document defined as the appropriate return value
according to the version of the Technical Specification it is testing against. 

Each key of the expected object can be assigned to either a hard value, such as a static string or expression,
or, alternatively, assigned to a function for more complex evaluation. All assertion functions must accept
one parameter, the value returned from the server for that property, and must return a `FunctionalAssertionResult`.
A sample return would be as such:

```javascript
return new FunctionalAssertionResult(
   AssertionFunction,
   [args],
   "expected value"
)
```

All of the assertion functions in utils.js have their bodies wrapped with a `FunctionalAssertionResult`, so 
you don't need to worry about it when calling them; you may return the result of that function directly.
If adding new utility functions, it is recommended that you wrap the function body in a `FunctionalAssertionResult`
like this:

```javascript
function assertSomeCondition(val, exp) {
   return new FunctionalAssertionResult(
      function() { /* function body with val and exp context available */ },
      [],
      exp
   )
}
```

As an example, in version 0.23 of the Technical Specification, we have the following service description specification for basic harvest:

```javascript
{

"doc_type":        "service_description",   

"doc_version":        "0.20.0",

"doc_scope":        "node",

"active":        true,

"service_id":        "<uniqueid>",       

"service_type":        "access",
     "service_name":    "Basic Harvest",   
     "service_description":    "Service to retreieve full JSON resource description documents from a node.  Patterned after OAI-PMH",
     "service_version":    "0.10.0",
     "service_endpoint":    "<node-service-endpoint-URL>",
     "service_auth":                // service authentication and authorization descriptions
     {
      "service_authz":    ["<authvalue>"],     // authz values for the service
      "service_key":        <T/F>,        // does service use an access key           
      "service_https":    <T/F>        // does service require https
     },
     "service_data":
     {

      "granularity":        "string",         // literal fixed vocabulary
                                              // "YYYY-MM-DD" (day granularity)	
                                              // or "YYYY-MM-DDThh:mm:ssZ" (second granularity)
      "flow_control":        FALSE,           // flow control not supported
      "setSpec":        NULL,         // sets are not supported
      "spec_kv_only":    <T/F>        // T to return only spec-defined key-value pairs
                                      // F to return all stored key-value pairs
                                      // optional, default F

      "metadataformats":            // array of supported metadata formats
      [
       {
       "metadataFormat":            // description of a metadata format

         {
            "metadataPrefix":     "LR_JSON_0.10.0"    // the only supported harvest form
                                                      // the Full OAI-PMH service will define
                                                      // schema and metadataNamespace
                                                      // where appropriate
         }
       }
      ]
    }
}
```

The corresponding expected object would look like this: 

```javascript
{
   "doc_type":             "service_description",  
   "doc_version":          function (val) { return isMatchingVersion(val, "0.20.0"); },
   "doc_scope":            "node",
   "active":               true,
   "service_id":           isNonEmptyString, 
   "service_type":         "access",
   "service_name":         "Basic Harvest",  
   "service_description":  function (val) { return isTypeOrUndefined(val, "string"); },
   "service_version":      function (val) { return isMatchingVersion(val, "0.10.0"); },
   "service_endpoint":     function (val) { return isValidServiceEndpoint(val, "harvest"); },
   "service_auth": {
      "service_authz":     validateAuthz,
      "service_key":       function (val) { return isTypeOrUndefined(val, "boolean"); },     
      "service_https":     function (val) { return isTypeOrUndefined(val, "boolean"); }
   },
   "service_data": {
      "granularity":       function (val) {
                               return new FunctionalAssertionResult(
                                 function(v) { return /^YYYY-MM-DD(Thh\:mm\:ssZ)?$/.test(v); },
                                 [val],
                                 "(regex) YYYY-MM-DD(Thh:mm:ssZ)?"
                               );
                           },
      "flow_control":      validateFlowControl,
      "id_limit":          validateFlowControlLimit,
      "doc_limit":         validateFlowControlLimit,
      "setSpec":           null,             
      "spec_kv_only":      function (val) { return isTypeOrUndefined(val, "boolean"); },  
      "metadataformats": [{
            "metadataFormat": {
               "metadataPrefix":    "LR_JSON_0.10.0"
            }
      }]
   }
};
```

Please refer to `utils.js` and `svc_desc.js` for further reading.