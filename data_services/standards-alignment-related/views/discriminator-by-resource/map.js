function(doc) {

    // !code lib/alignment.js

    try {
        if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
            var nodeTimestamp = convertDateToSeconds(doc);
            try {
                var parserDCT = function (conformsToText) {
                    var seen = {};
                    for (re in ASNPatterns){
                        var stds = conformsToText.match(ASNPatterns[re]);
                        for (s in stds) {
                            if (!seen[s]) {
                                emit([doc.resource_locator, stds[s]], nodeTimestamp);
                                seen[s] = 1;
                            }
                        }
                    }
                };


                Alignment.parseDCT_ConformsTo(doc.resource_data, parserDCT);
            } catch (e) {}

            try {
            if (typeof doc.resource_data == 'object') {
                var LRMIPackage = doc.resource_data; 
                for (idz in LRMIPackage.educationalAlignment) {
                    if (LRMIPackage.educationalAlignment[idz].targetUrl != null && typeof LRMIPackage.educationalAlignment[idz].targetUrl == 'object') {
                        for (idy in LRMIPackage.educationalAlignment[idz].targetUrl) {
                                emit([doc.resource_locator, LRMIPackage.educationalAlignment[idz].targetUrl[idy], nodeTimestamp]);
                        }
                    } else if (LRMIPackage.educationalAlignment[idz].targetUrl != null && typeof LRMIPackage.educationalAlignment[idz].targetUrl == 'string') {
                        emit([doc.resource_locator, LRMIPackage.educationalAlignment[idz].targetUrl, nodeTimestamp]);
                    }
                }
            }

            if (typeof doc.resource_data == 'string'){
                var LRMIPackage = JSON.parse(doc.resource_data); 
                for (idz in LRMIPackage.educationalAlignment) {
                    if (LRMIPackage.educationalAlignment[idz].targetUrl != null && typeof LRMIPackage.educationalAlignment[idz].targetUrl == 'string') {
                            emit([doc.resource_locator, LRMIPackage.educationalAlignment[idz].targetUrl, nodeTimestamp]);
                        } else if (LRMIPackage.educationalAlignment[idz].targetUrl != null && typeof LRMIPackage.educationalAlignment[idz].targetUrl == 'object') {
                            for (idy in LRMIPackage.educationalAlignment[idz].targetUrl) {
                                emit([doc.resource_locator, LRMIPackage.educationalAlignment[idz].targetUrl[idy], nodeTimestamp]);
                        }
                    }
                }
            }
            } catch (e) {}

            try {
                var seen = {};
                var parser = function (objStr, verb) {
                    for (re in ASNPatterns){
                        var stds = objStr.match(ASNPatterns[re]);
                        for (s in stds) {
                            if (!seen[s]) {
                                emit([doc.resource_locator, stds[s]], nodeTimestamp);
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