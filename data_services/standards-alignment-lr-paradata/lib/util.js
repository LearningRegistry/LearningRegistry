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
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 1 
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
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 1 
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
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 1 
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
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 1 
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
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 1 
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
                doc: getDoc,
                id: getId,
                either: getEither,
                group_length: 1 
            };
        } else {
            return null;
        }

    }

    var _ = require("lib/underscore-min");

    this.GroupIt = function(level, groups, row) {
        var row_group = _.first(row.key, level);
        log("same? "+JSON.stringify([groups.cur_group, row_group]));
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

    return this;
};