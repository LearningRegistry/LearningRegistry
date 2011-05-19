function(doc) {
    if(doc.doc_type == 'resource_data'){
        emit(doc.resource_locator, {_id:doc._id+'-timestamp',  
                                                    'resource_data':doc});  
    }
}
