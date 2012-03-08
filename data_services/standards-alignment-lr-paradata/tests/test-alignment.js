load("../../lib/jsunity-0.6.js");
jsUnity.log = function (obj) {
    print(obj);
}

var log = jsUnity.log;
function MockEmit() {
    this.emitted = [];
    this.cur_doc = null;
    this.cur_doc_id = null;
};

MockEmit.prototype.clear = function() {
    this.emitted = [];
    this.cur_doc = null;
    this.cur_doc_id = null;
};

MockEmit.prototype.setDoc = function(doc, with_doc) {
    if (with_doc) {
        this.cur_doc = doc;
    }
    this.cur_doc_id = doc._id;

};

MockEmit.prototype.emit = function(key, value){
    var obj = {"key": key, "value": value};
    if (this.cur_doc) {
        obj["doc"] = this.cur_doc;
    }
    if (this.cur_doc_id) {
        obj["id"] = this.cur_doc_id;
    }
    this.emitted.push(obj);
};

var mock_emit = new MockEmit();
var emit = function (key, value) {
    mock_emit.emit(key, value);
}

function LoadFn(path) {
    return eval(snarf(path));
}



load("data.js");


var t = {}; 

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

        log(JSON.stringify({"found":found}));

        t.assertTrue(found["http://purl.org/ASN/resources/S1000E0F"] > 0, "http://purl.org/ASN/resources/S1000E0F not found in return value.");
    }


    function test_map_discriminatorByResource() {

        load("../lib/alignment.js");
        var map_fn = LoadFn("../views/discriminator-by-resource/map.js");

        mock_emit.clear();
        mock_emit.setDoc(p_doc, false);
        map_fn(p_doc);

        log(JSON.stringify(mock_emit));

        for (var idx in mock_emit.emitted) {
            log(JSON.stringify(mock_emit.emitted[idx]));
        }

    }


}

jsUnity.attachAssertions(t);
var output = jsUnity.run(AlignmentTestSuite);
// print(JSON.stringify(output));
