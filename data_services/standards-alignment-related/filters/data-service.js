function(doc, req) {
    // !code lib/alignment.js
    if (doc.doc_type === "resource_data" && doc.resource_data) {
        var isGood = false;
        var parser = function(conformsTo) {
            for (re in ASNPatterns){
                if (ASNPatterns[re].test(conformsTo)) {
                    isGood = true;
                    //log("Good Document");
                    return true;
                }
            }
            return false;
        } 
        Alignment.parseDCT_ConformsTo(doc.resource_data, parser);
        return isGood;
    }
}