function(doc, req) {
	var resp = {
			"headers" : {
				"Content-Type" : "application/json"
			},
			"body" : {
				"OK" : true,
				"error" : "success",
				"document_results" : [
                  { 
                	  "doc_ID": "string",
                	  "OK" : true,
                	  "error" : "success"
                  }
				]
			}
	}
}