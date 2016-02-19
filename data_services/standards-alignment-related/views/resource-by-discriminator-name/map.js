function(doc) {

    // !code lib/alignment.js
    if (doc.doc_type == "resource_data" && doc.resource_data && doc.resource_locator && doc.node_timestamp) {
        var nodeTimestamp = convertDateToSeconds(doc);
                    try {
                if (typeof doc.resource_data == 'object') {
                var LRMIPackage = doc.resource_data; 
                for (idz in LRMIPackage.educationalAlignment) {
                    emit([LRMIPackage.educationalAlignment[idz].targetName, doc.resource_locator, nodeTimestamp],null);
                }
            }
                if (typeof doc.resource_data == 'string'){
                    var LRMIPackage = JSON.parse(doc.resource_data); 
                    for (idz in LRMIPackage.educationalAlignment) {
                        emit([LRMIPackage.educationalAlignment[idz].targetName, doc.resource_locator, nodeTimestamp],null);
                }
            }
            } catch (e) {}
    }   
    
}
