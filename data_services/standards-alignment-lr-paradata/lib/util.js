function GetViewInfo(req) {
    var vinfo = {};

    if (req && req.path) {
        vinfo["view"] = req.path[req.path.length-1];
    }

    
    return vinfo;
}

function RowParser(viewname) {

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

    if (viewname === "discriminator-by-resource") {
        return {
            discriminator: function(r) {
                return getKeyField(r, 1);
            },
            resource: function(r) {
                return getKeyField(r, 0);
            },
            timestamp: function(r) {
                return r.value;
            },
            doc: getDoc,
            id: getId
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
            id: getId
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
            id: getId
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
                return r.value;
            },
            doc: getDoc,
            id: getId
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
            id: getId
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
            id: getId
        };
    } else {
        return null;
    }

}