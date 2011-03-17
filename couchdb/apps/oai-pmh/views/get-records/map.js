function(doc) {
	if (doc.doc_ID) {
		emit(["by_doc_ID",doc.doc_ID], doc);
	}
	if (doc.resource_locator) {
		emit(["by_resource_locator",doc.resource_locator], doc);
	}
}