{
    "doc_type": 					"service_description",
    "doc_version": 				function (val) { return isMatchingVersion(val, "0.20.0"); },
	 "doc_scope": 					"node",
	 "active": 						true,
	 "service_id": 				isNonEmptyString,
	 "service_type": 				"distribute",
	 "service_name": 				"Resource Data Distribution",
	 "service_description": 	function (val) { return isTypeOrUndefined(val, "string"); },
	 "service_version": 			function (val) { return isMatchingVersion(val, "0.23.0"); },
	 "service_endpoint":			function (val) { return isValidServiceEndpoint(val, "distribute"); },
	 "service_auth": {
        "service_https": 		function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_key": 			function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_authz": 		validateAuthz
    }
}