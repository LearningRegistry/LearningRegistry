function(doc) {
	var makeValidSchema = function (origSchema) {		
		clean = origSchema.replace(/[^A-Za-z0-9\-_\.!~\*'\(\)]/g, '_');
		return clean;
	}
	
	if (doc.doc_type && doc.doc_type == "resource_data" && doc.payload_schema) {
		
		var okay = false;
		if (doc.payload_placement && doc.payload_placement == "inline" && doc.resource_data) {
			
			try {
				var data = doc.resource_data.replace(/^<\?xml\s+version\s*=\s*(["'])[^\1]+\1[^?]*\?>/, "");
				data = data.replace(/\s*<!DOCTYPE\s[^>]*>/m,"");
				var e4x = new XML(data);
				if (e4x) {
					okay = true;
				}
			} catch (error) {
				okay = false;
			}
			
		} else {
			okay = true;
		}
		
		if (okay) {
			for (var i = 0; i < doc.payload_schema.length; i++) {
				
				if (doc.doc_ID) {
					emit([makeValidSchema(doc.payload_schema[i]), "by_doc_ID",doc.doc_ID], (doc.payload_schema_locator ? doc.payload_schema_locator : null));
				}
				if (doc.resource_locator) {
					if (Object.prototype.toString.call( doc.resource_locator ) === '[object Array]') {
			            for (j=0; j<doc.resource_locator.length; j++) {
							emit([makeValidSchema(doc.payload_schema[i]), "by_resource_locator",doc.resource_locator[j]], (doc.payload_schema_locator ? doc.payload_schema_locator : null));
			            }
			        } else {
						emit([makeValidSchema(doc.payload_schema[i]), "by_resource_locator",doc.resource_locator], (doc.payload_schema_locator ? doc.payload_schema_locator : null));
			        }

				}
				
			}
		}
	}
}