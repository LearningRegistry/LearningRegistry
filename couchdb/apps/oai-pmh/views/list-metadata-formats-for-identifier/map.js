function(doc) {
	if (doc.payload_schema) {
		for (var i = 0; i < doc.payload_schema.length; i++) {
			
			if (doc.doc_ID) {
				emit([doc.payload_schema[i], "by_doc_ID",doc.doc_ID], null);
			}
			if (doc.resource_locator) {
				emit([doc.payload_schema[i], "by_resource_locator",doc.resource_locator], null);
			}
			
		}
	}
}