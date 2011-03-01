function(head, req) {
	/*
	 * This list is intended to be used with the metadata view, but could be used with any
	 * view that has an object as the value. 
	 * 
	 * URL parameters are used as a duck typing technique to filter.
	 * 
	 * Example:
	 * http://foo.com/db/_design/envelope/_list/filter/metadata?resource_type=NSDL&active=true
	 * 
	 * 
	 * // one
	 * {
	 * 		"active" : true,
	 * 		"resource_type" : "NSDL"
	 * }
	 * // two
	 * {
	 * 		"resource_type" : "OAI"
	 * }
	 * 
	 * // three
	 * {
	 * 		"active" : false,
	 * 		"resource_type" : "NSDL"
	 * }
	 * 
	 * // four
	 * {
	 * 		"active" : true,
	 * 		"resource_type" : "OAI"
	 * }
	 * 	
	 * 
	 * 
	 * The default behavior is to return results for documents that are missing fields.  Hence in the
	 * above example URL and dataset, one and two would both be returned, hence the object being returned
	 * should be normalized in structure to ensure the appropriate data is filtered.
	 * 
	 */
//	log("############ Begin of the metatdata list ############");
	var json = function () { require("lib/JSON-js/json2") };
	isArray = function(obj) {
		return obj.constructor.toString().indexOf("Array()") >= 0; 
	}
	
	isMatch = function(field, req, envelope) {
		pass = true;
		if (req.query[field] && envelope[field]) {
			pass = false;
			
			if (isArray(envelope[field])) {
//				log("it's and array");
				for (var i=0; i<envelope[field].length; i++) {
					log("["+ req.query[field] + "] == [" + envelope[field][i]+"]");
					if (req.query[field] == envelope[field][i]) {
//						log("pass");
						pass = true;
					} else { 
//						log("fail"); 
					}
					
				}
			} else {
//				log("not an array");
				if (req.query[field] !== envelope[field]) pass = false;
			}
		}
		return pass;
	}
	
	start({
		"headers": {
			"Content-Type": "application/json"
		}
	});
	send("[");
	while(row = getRow()) {
		envelope = row.key;
		
		pass = true;
		for (var field in req.query) {
			log("field: "+ field);
			pass &= isMatch(field, req, envelope);
		}
		if (pass) {
			send(JSON.stringify(envelope));
		}
	}
	send("]");
//	log("############ End of the metadata list ############");

}