function(doc) {
	if (doc.doc_type && doc.doc_type == "resource_data" && doc.node_timestamp) {
		emit(doc.node_timestamp, 1);
	}
}