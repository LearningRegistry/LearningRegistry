{
    "doc_type": 					"service_description",
    "doc_version": 				function (val) { return isMatchingVersion(val, "0.20.0"); },
	 "doc_scope": 					"node",
	 "active": 						true,
	 "service_id": 				isNonEmptyString,
	 "service_type": 				"publish",
	 "service_name": 				"Basic Publish",
	 "service_description": 	function (val) { return isTypeOrUndefined(val, "string"); },
    "service_version":  		function (val) { return isMatchingVersion(val, "0.23.0"); },
    "service_endpoint": 		function (val) { return isValidServiceEndpoint(val, "publish") },
    "service_auth": {
        "service_https": 		function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_key": 			function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_authz": 		validateAuthz
    },
    "service_data": {
        "doc_limit": 			function (val) { 
        									return new FunctionalAssertionResult(
        										function() { return typeof val == "number" && val > 0; },
        										[],
        										"positive integer"
     										);
  										},
        "msg_size_limit": 		function (val) { 
        									return new FunctionalAssertionResult(
        										function() { return typeof val == "number" && val > 0; },
        										[],
        										"positive integer"
     										);
  										}
    }
}