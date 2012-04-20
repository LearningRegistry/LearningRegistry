// # Copyright 2012 SRI International

// # Licensed under the Apache License, Version 2.0 (the "License"); you may not use this 
// # file except in compliance with the License. You may obtain a copy of the License at

// # http://www.apache.org/licenses/LICENSE-2.0

// # Unless required by applicable law or agreed to in writing, software distributed under the License 
// # is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
// # or implied. See the License for the specific language governing permissions and limitations under 
// # the License.

// # This project has been funded at least or in part with Federal funds from the U.S. Department of 
// # Education under Contract Number ED-04-CO-0040/0010. The content of this publication does not 
// # necessarily reflect the views or policies of the U.S. Department of Education nor does mention 
// # of trade names, commercial products, or organizations imply endorsement by the U.S. Government.



load("test-bootstrap.js")
load("data.js");

// assign assertion functions to convienience object.
var t = {}; 
jsUnity.attachAssertions(t);



function AlignmentTestSuite() {

    function setUp() {

    }

    function tearDown() {
        
    }

    function test_parseDCT_ConformsTo() {
        var expected = [
            "http://purl.org/ASN/resources/S11434E1",
            "http://purl.org/ASN/resources/S1143539",
            "http://purl.org/ASN/resources/S114353A",
            "http://purl.org/ASN/resources/S114353B",
            "http://purl.org/ASN/resources/S1143635",
            "http://purl.org/ASN/resources/S1143636",
            "http://purl.org/ASN/resources/S1143642",
            "http://purl.org/ASN/resources/S11435EC",
            "http://purl.org/ASN/resources/S11435ED",
            "http://purl.org/ASN/resources/S114364A",
            "http://purl.org/ASN/resources/S1143602"
        ];

        var innerStandards = [];
        var parser = function (stdString) {
            innerStandards.push(stdString);
        }

        load("../lib/alignment.js");

        var outerStandards = Alignment.parseDCT_ConformsTo(dc_doc.resource_data, parser);

        for (var i=0; i<innerStandards.length; i++) {
            t.assertTrue(outerStandards[innerStandards[i]] !== undefined);
        }

        for (var i=0; i<expected.length; i++) {
            t.assertTrue(outerStandards[expected[i]] !== undefined);
        }
    }


    function test_parseLRParadata() {

        var matches = 0;

        var parser = function(str, verb) {
            t.assertIdentical(Object.prototype.toString.apply(str), "[object String]");
            t.assertIdentical(Object.prototype.toString.apply(verb), "[object String]");

            var ret = {};
            for (var i=0; i<ASNPatterns.length; i++) {
                if (ASNPatterns[i].test(str)) {
                    matches++;
                    if (!ret[str]) {
                        ret[str] = 1;
                    } else {
                        ret[str]++;
                    }
                }
            }
            return ret;

        }

        load("../lib/alignment.js");
        var found = Alignment.parseLRParadata(p_doc.resource_data, parser);

        t.assertEqual(2, matches);

        log(JSON.stringify({"found":found}), LOG_LEVEL.DEBUG);

        t.assertTrue(found["http://purl.org/ASN/resources/S1000E0F"] > 0, "http://purl.org/ASN/resources/S1000E0F not found in return value.");
    }


    function test_map_discriminatorByResource() {

        var map_fn = GetMap("discriminator-by-resource");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit), LOG_LEVEL.DEBUG);
        t.assertEqual(2, mock_emit.emitted.length, "There should only be 2 elements emitted")

        for (var idx in mock_emit.emitted) {
            log(JSON.stringify(mock_emit.emitted[idx]), LOG_LEVEL.DEBUG);
        }

    }

    function test_map_discriminatorByResourceTS() {

        var map_fn = GetMap("discriminator-by-resource-ts");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit), LOG_LEVEL.DEBUG);

        t.assertEqual(1, mock_emit.emitted.length, "There should only be 1 element emitted")
        for (var idx in mock_emit.emitted) {
            log(JSON.stringify(mock_emit.emitted[idx]), LOG_LEVEL.DEBUG);
        }
    }

    function test_map_discriminatorByTS() {
        var map_fn = GetMap("discriminator-by-ts");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit), LOG_LEVEL.DEBUG);

        t.assertEqual(1, mock_emit.emitted.length, "There should only be 1 element emitted")
        
        var resource = p_doc.resource_locator;
        var verb = p_doc.resource_data.activity.verb.action;
        var asn = p_doc.resource_data.activity.related[0].id;
        var ts = Utils.convertDateToSeconds(p_doc.node_timestamp);

        var row = mock_emit.emitted[0];
        t.assertEqual(ts, row.key[0], "Timestamp doesn't match expected format.");
        t.assertEqual(verb, row.key[1][0], "Verb was expected");
        t.assertEqual(asn, row.key[1][1], "ASN was expected");
    }


    function test_map_resource_by_Discriminator() {
        var map_fn = GetMap("resource-by-discriminator");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit), LOG_LEVEL.DEBUG);
        t.assertEqual(2, mock_emit.emitted.length, "There should only be 2 elements emitted")

        for (var idx in mock_emit.emitted) {
            log(JSON.stringify(mock_emit.emitted[idx]), LOG_LEVEL.DEBUG);
        }

    }

    function test_map_resource_by_DiscriminatorTS() {
        var map_fn = GetMap("resource-by-discriminator-ts");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit), LOG_LEVEL.DEBUG);

        t.assertEqual(1, mock_emit.emitted.length, "There should only be 1 element emitted")
        for (var idx in mock_emit.emitted) {
            log(JSON.stringify(mock_emit.emitted[idx]), LOG_LEVEL.DEBUG);
        }
    }

    function test_map_resourceByTS() {
        var map_fn = GetMap("resource-by-ts");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit), LOG_LEVEL.DEBUG);

        t.assertEqual(1, mock_emit.emitted.length, "There should only be 1 element emitted")
        
        var resource = p_doc.resource_locator;
        var verb = p_doc.resource_data.activity.verb.action;
        var asn = p_doc.resource_data.activity.related[0].id;
        var ts = Utils.convertDateToSeconds(p_doc.node_timestamp);

        var row = mock_emit.emitted[0];
        t.assertEqual(ts, row.key[0], "Timestamp doesn't match expected format.");
        t.assertEqual(resource, row.key[1], "Resource locator was expected");
    }


    function test_list_toJSON() {

        this.test_map_discriminatorByResource();


        // var src = GetListSource("to-json");
        // var list_fn = Couch.compileFunction(src, couchdb_design_doc);
        var list_fn = GetList("to-json");

        mock_rows.setRows(mock_emit.emitted);
        mock_send.clear();

        list_fn(mock_data.head, mock_data.req);

        log(mock_send.join(), LOG_LEVEL.INFO);



    }
}

// logging enabled or disabled
log_active = true;

// this is the current logging level 
log_level = LOG_LEVEL.INFO;

// when calling log without some level, this is the default level assigned the message, such as what might
// appear in a map/reduce/show/list/filter function
default_log_level = LOG_LEVEL.ERROR;

// execute the tests
var output = jsUnity.run(AlignmentTestSuite);
// print(JSON.stringify(output));
