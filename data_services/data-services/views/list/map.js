function(doc) {
    if (doc._id.match(/^_design\// && doc.dataservice && doc.dataservice.name) {
        emit(doc.dataservice.name, null);
    }
}