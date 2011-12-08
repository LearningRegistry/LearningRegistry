{
	"doc_type": 			"policy_description",
	"doc_version": 		"0.10.0",
	"doc_scope": 			"network",
	"active": 				function (val) { 
									return new FunctionalAssertionResult(
										function() { return typeof val == "boolean"; },
										[],
										"boolean"
									);
								},
	"network_id": 			isNonEmptyString,
	"policy_id": 			isNonEmptyString,
	"policy_version": 	isNonEmptyString,
	"TTL": 					function (val) { 
									return new FunctionalAssertionResult(
										function() { return typeof val == "number" && parseInt(val).toString() != "NaN" && val > 0; },
										[],
										"positive integer"
									);
								}
}