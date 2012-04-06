exports.init = function(){

    this.GetViewInfo = function (req) {
        var vinfo = {};

        if (req && req.path) {
            vinfo["view"] = req.path[req.path.length-1];
        }

        
        return vinfo;
    }

    this.RowParser = function (viewname) {

        function getKeyField(r, i) {
            var key = r.key;
            return key[i];
        }

        function getDoc(r) {
            if (r.doc) {
                return r.doc;
            } else {
                return null;
            }
        }

        function getId(r) {
            if (r.id) {
                return r.id;
            } else {
                return null;
            }
        }

        function getEither(r) {
            if (r.doc)
                return r.doc;
            else if (r.id)
                return r.id;
            else
                return null;
        }

        if (viewname === "discriminator-by-resource") {
            return {
                discriminator: function(r) {
                    return getKeyField(r, 1);
                },
                resource: function(r) {
                    return getKeyField(r, 0);
                },
                timestamp: function(r) {
                    return getKeyField(r, 2);
                },
                showTimestamp: false,
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 2 
            };

        } else if (viewname === "discriminator-by-resource-ts") {
            return {
                discriminator: function(r) {
                    return getKeyField(r, 2);
                },
                resource: function(r) {
                    return getKeyField(r, 0);
                },
                timestamp: function(r) {
                    return getKeyField(r, 1);
                },
                showTimestamp: true,
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 3 
            };
        } else if (viewname === "discriminator-by-ts") {
            return {
                discriminator: function(r) {
                    return getKeyField(r, 1);
                },
                resource: function(r) {
                    return null;
                },
                timestamp: function(r) {
                    return getKeyField(r, 0);
                },
                showTimestamp: true,
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 2 
            };
        } else if (viewname === "resource-by-discriminator") {
            return {
                discriminator: function(r) {
                    return getKeyField(r, 0);
                },
                resource: function(r) {
                    return getKeyField(r, 1);
                },
                timestamp: function(r) {
                    return getKeyField(r, 2);
                },
                showTimestamp: false,
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 2 
            };
        } else if (viewname === "resource-by-discriminator-ts") {
            return {
                discriminator: function(r) {
                    return getKeyField(r, 0);
                },
                resource: function(r) {
                    return getKeyField(r, 2);
                },
                timestamp: function(r) {
                    return getKeyField(r, 1);
                },
                showTimestamp: true,
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 3 
            };
        } else if (viewname === "resource-by-ts") {
                    return {
                discriminator: function(r) {
                    return null;
                },
                resource: function(r) {
                    return getKeyField(r, 1);
                },
                timestamp: function(r) {
                    return getKeyField(r, 0);
                },
                showTimestamp: true,
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 2 
            };
        } else {
            return null;
        }

    }

    var _ = require("lib/underscore-min");

    this.GroupIt = function(level, groups, row) {
        var row_group = _.first(row.key, level);
        if (_.isEqual(groups.cur_group, row_group)) {
            groups.prev_group = null;
            groups.changed = false;
        } else {
            groups.prev_group = groups.cur_group;
            groups.cur_group = row_group;
            groups.changed = true;
        }
        return groups;
    }

    this.searchObjectForPattern = function(obj, regex) {
        var rs = {};
        var tmp = {};
        if (Object.prototype.toString.apply(obj) === "[object String]") {
            tmp = parser(obj.trim(), verb);
        } else if (Object.prototype.toString.apply(obj) === "[object Array]") {
            for (var j=0; j<obj.length; j++) {
                merge(searchObjectForPattern(obj[j], regex), tmp); 
            }
        } else if (Object.prototype.toString.apply(obj) === "[object Object]") {
            for (var key in obj) {
                merge(searchObjectForPattern(obj[key], regex), tmp);
            }
        } 
        if (tmp != undefined && tmp != null) {
            for (var key in tmp) {
                if (rs[key]) {
                    rs[key] += tmp[key];
                } else {
                    rs[key] = tmp[key];
                }
            }
        }

        return rs;
    };

    this.secondsToISODate = function(ts) {
        var ctime = new Date(ts*1000);
        return ctime.toISOString().replace(/\.000Z$/, "Z");
    };

    return this;
};