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

jsUnity.log = function(message) {
    if (typeof message == "xml") {
        message = message.toXMLString();
    } else if (typeof message != "string") {
        message = Couch.toJSON(message);
    }
    print(message);
}

// couchdb map & list should only call this with 1 argument
// tests can call with 2.
var log = function (message, level) {
    if (!level) {
        level = default_log_level;
    }
    if (log_active && level >= log_level) {
        jsUnity.log(message);
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

function MockRow() {
    this.rows = [];
    this.cur_index = -1;
}

MockRow.prototype.clear = function() {
    this.rows = [];
}

MockRow.prototype.setRows = function(rows) {
    this.rows = rows;
}

MockRow.prototype.getRow = function() {
    return this.rows.pop();
}

var mock_rows = new MockRow();
var getRow = function() {
    return mock_rows.getRow();
}



function MockSend() {
    this.sent = [];
}

MockSend.prototype.clear = function() {
    this.sent = [];
}

MockSend.prototype.send = function(obj) {
    this.sent.push(obj);
}

MockSend.prototype.join = function() {
    return this.sent.join("\n");
}

var mock_send = new MockSend();
var send = function(obj) {
    mock_send.send(obj);
}


var Utils = {

    convertDateToSeconds: function(timestamp){
        return Math.floor(Date.parse(timestamp)/1000);
    },

    isArray: function (obj) {
        return toString.call(obj) === "[object Array]";
    },

    sum: function (values) {
        var rv = 0;
        for (var i in values) {
            rv += values[i];
        }
        return rv;
    }
}

var couchdb_design_doc = undefined;
if (arguments.length == 1) {
    print("Loading external file: "+arguments[0])
    load(arguments[0]);
} else {
    print("No Additional files loaded.")
}

function reduce_count(keys, values, rereduce) {
    return values.length;
}


// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy of
// the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.


var Mime = (function() {
  // registerType(name, mime-type, mime-type, ...)
  // 
  // Available in query server sandbox. TODO: The list is cleared on reset.
  // This registers a particular name with the set of mimetypes it can handle.
  // Whoever registers last wins.
  // 
  // Example: 
  // registerType("html", "text/html; charset=utf-8");

  var mimesByKey = {};
  var keysByMime = {};
  function registerType() {
    var mimes = [], key = arguments[0];
    for (var i=1; i < arguments.length; i++) {
      mimes.push(arguments[i]);
    };
    mimesByKey[key] = mimes;
    for (var i=0; i < mimes.length; i++) {
      keysByMime[mimes[i]] = key;
    };
  }

  // Some default types
  // Ported from Ruby on Rails
  // Build list of Mime types for HTTP responses
  // http://www.iana.org/assignments/media-types/
  // http://dev.rubyonrails.org/svn/rails/trunk/actionpack/lib/action_controller/mime_types.rb

  registerType("all", "*/*");
  registerType("text", "text/plain; charset=utf-8", "txt");
  registerType("html", "text/html; charset=utf-8");
  registerType("xhtml", "application/xhtml+xml", "xhtml");
  registerType("xml", "application/xml", "text/xml", "application/x-xml");
  registerType("js", "text/javascript", "application/javascript", "application/x-javascript");
  registerType("css", "text/css");
  registerType("ics", "text/calendar");
  registerType("csv", "text/csv");
  registerType("rss", "application/rss+xml");
  registerType("atom", "application/atom+xml");
  registerType("yaml", "application/x-yaml", "text/yaml");
  // just like Rails
  registerType("multipart_form", "multipart/form-data");
  registerType("url_encoded_form", "application/x-www-form-urlencoded");
  // http://www.ietf.org/rfc/rfc4627.txt
  registerType("json", "application/json", "text/x-json");
  
  
  var mimeFuns = [];
  function provides(type, fun) {
    Mime.providesUsed = true;
    mimeFuns.push([type, fun]);
  };

  function resetProvides() {
    // set globals
    Mime.providesUsed = false;
    mimeFuns = [];
    Mime.responseContentType = null;  
  };

  function runProvides(req, ddoc) {
    var supportedMimes = [], bestFun, bestKey = null, accept = req.headers["Accept"];
    if (req.query && req.query.format) {
      bestKey = req.query.format;
      Mime.responseContentType = mimesByKey[bestKey][0];
    } else if (accept) {
      // log("using accept header: "+accept);
      mimeFuns.reverse().forEach(function(mimeFun) {
        var mimeKey = mimeFun[0];
        if (mimesByKey[mimeKey]) {
          supportedMimes = supportedMimes.concat(mimesByKey[mimeKey]);
        }
      });
      Mime.responseContentType = Mimeparse.bestMatch(supportedMimes, accept);
      bestKey = keysByMime[Mime.responseContentType];
    } else {
      // just do the first one
      bestKey = mimeFuns[0][0];
      Mime.responseContentType = mimesByKey[bestKey][0];
    }

    if (bestKey) {
      for (var i=0; i < mimeFuns.length; i++) {
        if (mimeFuns[i][0] == bestKey) {
          bestFun = mimeFuns[i][1];
          break;
        }
      };
    };

    if (bestFun) {
      return bestFun.call(ddoc);
    } else {
      var supportedTypes = mimeFuns.map(function(mf) {return mimesByKey[mf[0]].join(', ') || mf[0]});
      throw(["error","not_acceptable",
        "Content-Type "+(accept||bestKey)+" not supported, try one of: "+supportedTypes.join(', ')]);
    }
  };

  
  return {
    registerType : registerType,
    provides : provides,
    resetProvides : resetProvides,
    runProvides : runProvides
  }  
})();



// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy of
// the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.
var resolveModule = function(names, mod, root) {
    if (names.length == 0) {
        if (typeof mod.current != "string") {
            throw ["error", "invalid_require_path", 'Must require a JavaScript string, not: ' + (typeof mod.current)];
        }
        return {
            current: mod.current,
            parent: mod.parent,
            id: mod.id,
            exports: {}
        }
    }
    // we need to traverse the path
    var n = names.shift();
    if (n == '..') {
        if (!(mod.parent && mod.parent.parent)) {
            throw ["error", "invalid_require_path", 'Object has no parent ' + JSON.stringify(mod.current)];
        }
        return resolveModule(names, {
            id: mod.id.slice(0, mod.id.lastIndexOf('/')),
            parent: mod.parent.parent,
            current: mod.parent.current
        });
    } else if (n == '.') {
        if (!mod.parent) {
            throw ["error", "invalid_require_path", 'Object has no parent ' + JSON.stringify(mod.current)];
        }
        return resolveModule(names, {
            parent: mod.parent,
            current: mod.current,
            id: mod.id
        });
    } else if (root) {
        mod = {
            current: root
        };
    }
    if (mod.current[n] === undefined) {
        throw ["error", "invalid_require_path", 'Object has no property "' + n + '". ' + JSON.stringify(mod.current)];
    }
    return resolveModule(names, {
        current: mod.current[n],
        parent: mod,
        id: mod.id ? mod.id + '/' + n : n
    });
};



var Couch = {
  // moving this away from global so we can move to json2.js later
  toJSON : function (val) {
    return JSON.stringify(val);
  },
  compileFunction : function(source, ddoc) {    
    if (!source) throw(["error","not_found","missing function"]);
    try {
      if (sandbox) {
        if (ddoc) {
          if (!ddoc._module_cache) {
            ddoc._module_cache = {};
          }
          var require = function(name, module) {
            module = module || {};
            var newModule = resolveModule(name.split('/'), module.parent, ddoc);
            if (!ddoc._module_cache.hasOwnProperty(newModule.id)) {
              // create empty exports object before executing the module,
              // stops circular requires from filling the stack
              ddoc._module_cache[newModule.id] = {};
              var s = "function (module, exports, require) { " + newModule.current + " }";
              try {
                var func = sandbox ? evalcx(s, sandbox) : eval(s);
                func.apply(sandbox, [newModule, newModule.exports, function(name) {
                  return require(name, newModule);
                }]);
              } catch(e) { 
                throw ["error","compilation_error","Module require('"+name+"') raised error "+e.toSource()]; 
              }
              ddoc._module_cache[newModule.id] = newModule.exports;
            }
            return ddoc._module_cache[newModule.id];
          }
          sandbox.require = require;
        }
        var functionObject = evalcx(source, sandbox);
      } else {
        var functionObject = eval(source);
      }
    } catch (err) {
      throw(["error", "compilation_error", err.toSource() + " (" + source + ")"]);
    };
    if (typeof(functionObject) == "function") {
      return functionObject;
    } else {
      throw(["error","compilation_error",
        "Expression does not eval to a function. (" + source.toSource() + ")"]);
    };
  },
  recursivelySeal : function(obj) {
    // seal() is broken in current Spidermonkey
    try {
      seal(obj);
    } catch (x) {
      // Sealing of arrays broken in some SpiderMonkey versions.
      // https://bugzilla.mozilla.org/show_bug.cgi?id=449657
    }
    for (var propname in obj) {
      if (typeof obj[propname] == "object") {
        arguments.callee(obj[propname]);
      }
    }
  }
}


// Licensed under the Apache License, Version 2.0 (the "License"); you may not
// use this file except in compliance with the License. You may obtain a copy of
// the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

var sandbox = null;

function init_sandbox() {
  try {
    // if possible, use evalcx (not always available)
    sandbox = evalcx('');
    sandbox.emit = emit;
    sandbox.sum = Utils.sum;
    sandbox.log = log;
    sandbox.toJSON = Couch.toJSON;
    sandbox.JSON = JSON;
    sandbox.provides = Mime.provides;
    sandbox.registerType = Mime.registerType;
    // sandbox.start = Render.start;
    sandbox.send = send;
    sandbox.getRow = getRow;
    sandbox.isArray = Utils.isArray;
  } catch (e) {
    log(e.toSource());
  }
};
init_sandbox();


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

function GetMap(name) {
    return eval(GetMapSource(name));
}

function GetMapSource(name) {
    var view = couchdb_design_doc.views[name];
    return view.map;
}

function GetReduce(name) {
    var view = couchdb_design_doc.views[name];

    if (/^(_count)$/.test(view.trim())) {
        return reduce_count;
    } else {
        return eval(view.reduce);
    }
}

function GetListSource(name) {
    var list = couchdb_design_doc.lists[name];
    return list;
}

function GetList(name) {
    var src = GetListSource("to-json");
    var list_fn = Couch.compileFunction(src, couchdb_design_doc);
    return list_fn;
}


function GetFilterSource(name) {
    var filt = couchdb_design_doc.filters[name];
    return filt;
}

function GetFilter(name) {
    var src = GetFilter(name);
    var filt_fn = Couch.compileFunction(src.couchdb_design_doc);
    return filt_fn;
}