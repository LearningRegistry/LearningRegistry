function(doc) {
    if(doc.doc_type == 'resource_data'){
        emit(doc.resource_locator,  null);  
    }
}
