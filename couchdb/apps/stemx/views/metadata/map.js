function(doc) {
	/*
	 * This map creates a view of only metadata typed documents. Very loose duck typing used to do this.
	 * In a production environment, you'd do more validation.
	 */
	
	/* if this isn't metadata, then just skip */
	if (!(doc.doc_type && doc.doc_type === "resource_data" && 
			doc.doc_version && doc.doc_version === "0.10.0" &&
			doc.resource_data_type && doc.resource_data_type === "metadata")) {
		return;
	}
	
//	emit(doc.resource_data_type, doc);
	emit(doc,null);
}