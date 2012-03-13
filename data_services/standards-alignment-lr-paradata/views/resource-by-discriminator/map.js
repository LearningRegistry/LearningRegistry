function(doc) {
    // !code lib/alignment.js
    try {
        if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
            var nodeTimestamp = convertDateToSeconds(doc);
            var seen = {};
            var parser = function (objStr, verb) {
                for (re in ASNPatterns){
                    var stds = objStr.match(ASNPatterns[re]);
                    for (s in stds) {
                        if (!seen[s]) {
                            emit([[verb, stds[s]], doc.resource_locator], nodeTimestamp);
                            emit([[stds[s], verb], doc.resource_locator], nodeTimestamp);
                            seen[s] = 1;
                        }
                    }
                }
            };

            Alignment.parseLRParadata(doc.resource_data, parser);
        }   
    
    } catch (error) {
            log("error:"+error);
    }
}