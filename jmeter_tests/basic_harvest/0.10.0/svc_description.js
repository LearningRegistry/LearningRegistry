{
	"doc_type":					"service_description",	
 	"doc_version":				function (val) { return isMatchingVersion(val, "0.20.0"); },
 	"doc_scope":				"node",
 	"active":					true,
	"service_id":				isNonEmptyString,	
 	"service_type":			"access",
	"service_name":			"Basic Harvest",	
	"service_description":	function (val) { return isTypeOrUndefined(val, "string"); },
	"service_version":		function (val) { return isMatchingVersion(val, "0.10.0"); },
	"service_endpoint":		function (val) { return isValidServiceEndpoint(val, "harvest"); },
	"service_auth": {
		"service_authz":		validateAuthz,
	   "service_key":			function (val) { return isTypeOrUndefined(val, "boolean"); },		
	   "service_https":		function (val) { return isTypeOrUndefined(val, "boolean"); }
	},
	"service_data": {
	 	"granularity":			function (val) {
	 									 return new FunctionalAssertionResult(
	 									 	function(v) { return /^YYYY-MM-DD(Thh\:mm\:ssZ)?$/.test(v); },
	 									 	[val],
	 									 	"(regex) YYYY-MM-DD(Thh:mm:ssZ)?"
	 									 );
								 	},
	  	"flow_control":		validateFlowControl,
	  	"id_limit": 			validateFlowControlLimit,
	  	"doc_limit": 			validateFlowControlLimit,
	  	"setSpec":				null,					
	  	"spec_kv_only":		function (val) { return isTypeOrUndefined(val, "boolean"); },	
	  	"metadataformats": [{
		  		"metadataFormat": {
		    		"metadataPrefix": 	"LR_JSON_0.10.0"
		   	}
   	}]
	}
};