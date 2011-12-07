{
    "doc_type": 					"service_description",
    "doc_version": 				function (val) { return isMatchingVersion(val, "0.20.0"); },
    "doc_scope": 					"node",
    "active": 						true,
    "service_id": 				isNonEmptyString,
    "service_type": 				"administrative",
    "service_name": 				"Network Node Status",
    "service_description": 	function (val) { return isTypeOrUndefined(val, "string"); },
    "service_version": 			function (val) { return isMatchingVersion(val, "0.23.0"); },
    "service_endpoint": 		function (val) { return isValidServiceEndpoint(val, "status"); },
    "service_auth": {
        "service_authz": 		validateAuthz,
        "service_key": 			function (val) { return isTypeOrUndefined(val,"boolean"); },
        "service_https": 		function (val) { return isTypeOrUndefined(val,"boolean"); }
    }
}