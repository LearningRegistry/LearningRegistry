{
	"doc_type":					"service_description",	
 	"doc_version":				function (val) { return isMatchingVersion(val, "0.20.0"); },
 	"doc_scope":				"node",
 	"active":					true,
 	"service_id":				isNonEmptyString,
 	"service_type":			"access",
	"service_name":			"OAI-PMH Harvest",	
	"service_description":	function (val) { return isTypeOrUndefined(val, "string"); },
	"service_version":		function (val) { return isMatchingVersion(val, "0.10.0"); },
	"service_endpoint":		function (val) { return isValidServiceEndpoint(val, "OAI\-PMH"); },
	"service_auth":				
	{
		"service_authz":		validateAuthz, 	
	   "service_key":			function (val) { return isTypeOrUndefined(val, "boolean"); },				
	   "service_https":		function (val) { return isTypeOrUndefined(val, "boolean"); },		
	},
	"service_data":
	{
 		"version": 				"OAI-PMH 2.0",
 		"schemalocation":		function (val) { 
 										return new FunctionalAssertionResult(
 											function() { return /^http(s)?\:\/\/(.)*\.(xsd|XSD)$/.test(val); },
 											[],
 											"valid url pointing to an .xsd file"
 										);
									},
	  	"spec_kv_only":		function (val) { return isTypeOrUndefined(val, "boolean"); }	
	}
};