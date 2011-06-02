function(doc) {

	if (doc.doc_type && doc.doc_type=="resource_data" && doc.node_timestamp && doc.payload_schema) {
		for (var i = 0; i < doc.payload_schema.length; i++) {
			ts = doc.node_timestamp.replace(/\.[0-9]+Z/gi, "");
			emit([doc.payload_schema[i],ts], null);
		}
	}
}