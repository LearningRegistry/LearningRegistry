function(doc) {
    if(doc.doc_type == 'resource_data'){
        emit(decodeURI(doc.resource_locator),  null);  
    }
}
