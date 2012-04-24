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



load("../../lib/jsunity-0.6.js");
load("../../lib/test-common.js");

jsUnity.assertions.assertNotUndefined(couchdb_design_doc, "couchdb_design_doc is not defined.");
jsUnity.assertions.assertNotUndefined(couchdb_design_doc["_id"], "couchdb_design_doc is not a CouchDB Design Doc.");

// BEGIN: MOVED TO ../../lib/test-common.js
// function GetMap(name) {
//     return eval(GetMapSource(name));
// }

// function GetMapSource(name) {
//     var view = couchdb_design_doc.views[name];
//     return view.map;
// }

// function GetReduce(name) {
//     var view = couchdb_design_doc.views[name];

//     if (/^(_count)$/.test(view.trim())) {
//         return reduce_count;
//     } else {
//         return eval(view.reduce);
//     }
// }

// function GetListSource(name) {
//     var list = couchdb_design_doc.lists[name];
//     return list;
// }

// function GetList(name) {
//     var src = GetListSource("to-json");
//     var list_fn = Couch.compileFunction(src, couchdb_design_doc);
//     return list_fn;
// }


// function GetFilterSource(name) {
//     var filt = couchdb_design_doc.filters[name];
//     return filt;
// }

// function GetFilter(name) {
//     var src = GetFilter(name);
//     var filt_fn = Couch.compileFunction(src.couchdb_design_doc);
//     return filt_fn;
// }

// END: MOVED TO ../../lib/test-common.js

// Deprecating - don't use
// function LoadCodeMacros(f_string) {
//     var code_regex = /(\/\/|#)\ ?!code (.*)/;
//     var match = null;
//     while (matches = code_regex.exec(f_string)) {
//         var f_path = matches[2];
//         var f_contents = snarf("../" + f_path);
//         f_string = f_string.replace(new RegExp(matches[0], "g"), f_contents);
//     }
//     return f_string;
// }

// //  For some reason... this function has to be here for it to work.
// function LoadFn(path) {
//     return eval(LoadCodeMacros(snarf(path)));
// }