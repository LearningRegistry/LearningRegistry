function(doc) {
	if (doc.node_timestamp) {
		emit(doc.node_timestamp, 1);
	}
}