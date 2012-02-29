function(doc) {

    // !code lib/alignment.js

    if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
        var parser = function (conformsToText) {
            var seen = {};            
            var nodeTimestamp = convertDateToSeconds(doc);
            for (re in ASNPatterns){
                var stds = conformsToText.match(ASNPatterns[re]);                    
                for (s in stds) {
                    if (!seen[s]) {

                        emit([stds[s], nodeTimestamp, doc.resource_locator], null);
                        seen[s] = 1;
                    }
                }
            }
        };

        Alignment.parseDCT_ConformsTo(doc.resource_data, parser);
    }   
    
}