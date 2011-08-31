function(doc) {
	if (doc.doc_type && doc.doc_type == "resource_data" && doc.payload_schema) {
		for (var i = 0; i < doc.payload_schema.length; i++) {
			
			if (doc.doc_ID) {
				emit([doc.payload_schema[i], "by_doc_ID",doc.doc_ID], (doc.payload_schema_locator ? doc.payload_schema_locator : null));
			}
			if (doc.resource_locator) {
				emit([doc.payload_schema[i], "by_resource_locator",doc.resource_locator], (doc.payload_schema_locator ? doc.payload_schema_locator : null));
			}
			
		}
	}
}