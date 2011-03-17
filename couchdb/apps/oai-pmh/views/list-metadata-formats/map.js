function(doc) {
	if (doc.payload_schema) {
		for (var i = 0; i < doc.payload_schema.length; i++) {
			emit(doc.payload_schema[i], 1);
		}
	}
}