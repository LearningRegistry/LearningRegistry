function(doc) {

    // !code lib/alignment.js

    try {
        if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
            var nodeTimestamp = convertDateToSeconds(doc);
            var seen = false;
            var parser = function (conformsToText) { 
                if (seen) return;
                
                for (re in ASNPatterns){
                    var stds = conformsToText.match(ASNPatterns[re]);
                    for (s in stds) {
                        if (!seen) {
                            emit([nodeTimestamp, doc.resource_locator], null);
                            seen = true;
                            break;
                        }
                    }
                    if (seen) break;
                }
            };

            Alignment.parseDCT_ConformsTo(doc.resource_data, parser);
        }   
    
    } catch (error) {
            log("error:"+error);
    }
}