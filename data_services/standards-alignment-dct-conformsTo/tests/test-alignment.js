load("test-bootstrap.js");
load("data.js");


var t = {}; 
jsUnity.attachAssertions(t);

function AlignmentTestSuite() {

    function setUp() {

    }

    function tearDown() {
        
    }

    function test_lib_alignment_parseDCT_ConformsTo() {
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


    function test_lib_alignment_parseLRParadata() {

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

        log(JSON.stringify({"found":found}));

        t.assertTrue(found["http://purl.org/ASN/resources/S1000E0F"] > 0, "http://purl.org/ASN/resources/S1000E0F not found in return value.");
    }


}

// logging enabled or disabled
log_active = true;

// this is the current logging level 
log_level = LOG_LEVEL.INFO;

// when calling log without some level, this is the default level assigned the message, such as what might
// appear in a map/reduce/show/list/filter function
default_log_level = LOG_LEVEL.ERROR;

var output = jsUnity.run(AlignmentTestSuite);
// print(JSON.stringify(output));
