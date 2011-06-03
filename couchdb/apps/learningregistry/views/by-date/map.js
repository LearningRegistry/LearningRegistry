function(doc) {
    if(doc.doc_type == 'resource_data')
    {
        emit(doc.node_timestamp, null);
    }
}
