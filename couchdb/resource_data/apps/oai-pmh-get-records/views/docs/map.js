function(doc) {

	if (doc.doc_type && doc.doc_type=="resource_data" && doc.node_timestamp && doc.payload_schema) {
		
		var okay = false;
		if (doc.payload_placement && doc.payload_placement == "inline" && doc.resource_data) {
			
			try {
				var e4x = new XML(doc.resource_data.replace(/^<\?xml\s+version\s*=\s*(["'])[^\1]+\1[^?]*\?>/, ""));
				if (e4x) {
					okay = true;
				}
			} catch (error){
				okay = false;
			}
			
		} else {
			okay = true;
		}
		
		if (okay) {
			if (doc.doc_ID) {
				emit(["by_doc_ID",doc.doc_ID], null);
			}
			if (doc.resource_locator) {
				emit(["by_resource_locator",doc.resource_locator], null);
			}
		}
	}
}