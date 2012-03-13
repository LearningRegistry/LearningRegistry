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




var LOG_LEVEL = {
    ERROR: 10,
    WARN: 8,
    INFO : 5,
    DEBUG: 3,
    TRACE: 0 
}

// loggineg enabled or disabled
var log_active = true;

// this is the current logging level 
var log_level = LOG_LEVEL.INFO;

// when calling log without some level, this is the default level assigned the message.
var default_log_level = LOG_LEVEL.ERROR;

jsUnity.log = function (obj) {
    print(obj);
}

// couchdb map & list should only call this with 1 argument
// tests can call with 2.
var log = function (obj, level) {
    if (!level) {
        level = default_log_level;
    }
    if (log_active && level >= log_level) {
        jsUnity.log(obj);
    }
}

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

var Utils = {

    convertDateToSeconds: function(timestamp){
        return Math.floor(Date.parse(timestamp)/1000);
    }
}
var couchdb_design_doc = undefined;
if (arguments.length == 1) {
    print("Loading external file: "+arguments[0])
    load(arguments[0]);
} else {
    print("No Additional files loaded.")
}
