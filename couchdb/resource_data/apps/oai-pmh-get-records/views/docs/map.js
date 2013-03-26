function(doc) {

	if (doc.doc_type && doc.doc_type=="resource_data" && doc.node_timestamp && doc.payload_schema) {
		
		var okay = false;
		if (doc.payload_placement && doc.payload_placement == "inline" && doc.resource_data) {
			
			try {
				var data = doc.resource_data.replace(/^<\?xml\s+version\s*=\s*(["'])[^\1]+\1[^?]*\?>/, "");
				data = data.replace(/\s*<!DOCTYPE\s[^>]*>/m,"");
				var e4x = new XML(data);				
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
				if (Object.prototype.toString.call( doc.resource_locator ) === '[object Array]') {
		            for (i=0; i<doc.resource_locator.length; i++) {
		                emit(["by_resource_locator",doc.resource_locator[i]],  null);  
		            }
		        } else {
		            emit(["by_resource_locator",doc.resource_locator], null);  
		        }
			}
		}
	}
}