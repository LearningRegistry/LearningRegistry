function(doc, req) {
    // !code lib/alignment.js
    if (doc.doc_type === "resource_data" && doc.resource_data) {
        var isGood = false;
        var parser = function(objStr, verb) {
            for (re in ASNPatterns){
                if (ASNPatterns[re].test(objStr)) {
                    isGood = true;
                    //log("Good Document");
                    return true;
                }
            }
            return false;
        } 
        Alignment.parseLRParadata(doc.resource_data, parser);
        return isGood;
    }
}