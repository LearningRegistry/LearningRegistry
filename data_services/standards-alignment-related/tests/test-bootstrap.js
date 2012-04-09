load("../../lib/jsunity-0.6.js");
load("../../lib/test-common.js");

jsUnity.assertions.assertNotUndefined(couchdb_design_doc, "couchdb_design_doc is not defined.");
jsUnity.assertions.assertNotUndefined(couchdb_design_doc["_id"], "couchdb_design_doc is not a CouchDB Design Doc.");
