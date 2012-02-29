function(doc) {

    // !code lib/alignment.js

    try {
        if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
            var parser = function (conformsToText) {
                var seen = {};
                for (re in ASNPatterns){
                    var stds = conformsToText.match(ASNPatterns[re]);
                    for (s in stds) {
                        if (!seen[s]) {
                            emit([stds[s], doc.node_timestamp, doc.resource_locator], null);
                            seen[s] = 1;
                        }
                    }
                }
            };

            Alignment.parseDCT_ConformsTo(doc.resource_data, parser);
        }   
    
    } catch (error) {
            log("error:"+error);
    }
}