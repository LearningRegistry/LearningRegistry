{
    "doc_type": 					"service_description",
    "doc_version": 				function (val) { return isMatchingVersion(val, "0.20.0"); },
	 "doc_scope": 					"node",
	 "active": 						true,
	 "service_id": 				isNonEmptyString,
	 "service_type": 				"access",
	 "service_name": 				"SWORD APP Publish V1.3",
	 "service_description": 	function (val) { return isTypeOrUndefined(val, "string"); },
    "service_version":  		function (val) { return isMatchingVersion(val, "0.23.0"); },
    "service_endpoint": 		function (val) { return isValidServiceEndpoint(val, "swordservice"); },
    "service_auth": {
        "service_https": 		function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_key": 			function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_authz": 		validateAuthz
    },
    "service_data": {
        "version" : 				function (val) { return isMatchingVersion(val, "1.3"); }
    }
}