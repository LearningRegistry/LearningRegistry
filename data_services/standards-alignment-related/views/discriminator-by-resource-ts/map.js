function(doc) {

    // !code lib/alignment.js

    try {
        if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
            var nodeTimestamp = convertDateToSeconds(doc);
            try {
                var parser = function (conformsToText) {
                    var seen = {};
                    for (re in ASNPatterns){
                        var stds = conformsToText.match(ASNPatterns[re]);
                        for (s in stds) {
                            if (!seen[s]) {
                                emit([doc.resource_locator, nodeTimestamp, stds[s]], null);
                                seen[s] = 1;
                            }
                        }
                    }
                };

                Alignment.parseDCT_ConformsTo(doc.resource_data, parser);
            } catch (e) {}
        
            try {
                var seen = {};
                var parser = function (objStr, verb) {
                    for (re in ASNPatterns){
                        var stds = objStr.match(ASNPatterns[re]);
                        for (s in stds) {
                            if (!seen[s]) {
                                emit([doc.resource_locator, nodeTimestamp, stds[s]], null);
                                seen[s] = 1;
                            }
                        }
                    }
                };

                Alignment.parseLRParadata(doc.resource_data, parser);
            } catch (e) {}
        }   
    
    } catch (error) {
            log("error:"+error);
    }
}