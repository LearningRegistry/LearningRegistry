function(doc) {
    if(doc.doc_type == 'resource_data')
    {
    	ts = doc.node_timestamp.replace(/\.[0-9]+Z/gi, "");
        emit(ts, null);
    }
}
	
