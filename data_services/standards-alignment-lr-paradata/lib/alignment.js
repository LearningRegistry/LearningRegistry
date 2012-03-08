var ASNPatterns = [
    /https?:\/\/purl\.org\/ASN\/resources\/[A-Z0-9]+/g,
    /https?:\/\/asn\.jesandco\.org\/resources\/[A-Z0-9]+/g
];

var Alignment = {
    
    parseDCT_ConformsTo: function(resource_data, parser) {
        var stds = {};
        try {
                var nsdl = new XML(resource_data);
                var dct = new Namespace("http://purl.org/dc/terms/");

                conformsToElems = nsdl..dct::conformsTo

                for (idx in conformsToElems) {
                    if (!stds[conformsToElems[idx].toString().trim()]) {
                        var shouldBreak = parser(conformsToElems[idx].toString().trim());
                        stds[conformsToElems[idx].toString().trim()] = 1;
                        if (shouldBreak) {
                            break;
                        }
                    } 
                }

        } catch (error) {
            log(error);
        }
        return stds;
    },

    parseLRParadata: function(resource_data, parser) {
        var result = null;
        try {

            var verb = resource_data.activity.verb.action;

            var merge = function(a, b) {
                if (b === null && a !== null) {
                    b = a;
                    return;
                } else if (a === null) {
                    return;
                } else {
                    for (var key in a) {
                        if (b[key]) {
                            b[key] += a[key];
                        } else {
                            b[key] = a[key];
                        }
                    }
                }
            }

            var searchObjectForPattern = function(obj, regex) {
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

            result = searchObjectForPattern(resource_data,ASNPatterns);
        } catch (error) {
            log(error);
        } finally {
            return result;
        }

    }

};
function convertDateToSeconds(doc){
    return Math.floor(Date.parse(doc.node_timestamp)/1000);
}
