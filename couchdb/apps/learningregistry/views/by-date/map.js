function(doc) {
    if(doc.doc_type == 'resource_data_timestamp')
    {
        emit(doc.node_timestamp, null);
    }
}
