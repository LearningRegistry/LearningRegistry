{
    "doc_type": 				  "service_description",
    "doc_version": 			  function (val) { return isMatchingVersion(val, "0.20.0"); },
	 "doc_scope": 				  "node",
	 "active": 					  true,
	 "service_id": 			  isNonEmptyString,
	 "service_type":			  "access",
	 "service_name": 			  "Basic Obtain",
	 "service_description":   function (val) { return isTypeOrUndefined(val, "string"); },
    "service_version":		  function (val) { return isMatchingVersion(val, "0.21.0"); },
    "service_endpoint": 	  function (val) { return isValidServiceEndpoint(val, "obtain"); },
    "service_auth": {
        "service_https": 	  function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_key": 		  function (val) { return isTypeOrUndefined(val, "boolean"); },
        "service_authz": 	  validateAuthz
    },
    "service_data": {
        "version" : 			  function (val) { return isMatchingVersion(val, "1.3"); },
        "flow_control":		  validateFlowControl,	
	  	  "id_limit": 			  validateFlowControlLimit,
	  	  "doc_limit": 		  validateFlowControlLimit,
	  	  "spec_kv_only":		  function (val) { return isTypeOrUndefined(val, "boolean"); }
    }
}