function isValidServiceEndpoint(val, endpointVal) {
	return new FunctionalAssertionResult(
		//TODO: find reliable regex for validating urls
		function(v) { return new RegExp("^(.*)\/"+endpointVal+"$").test(v); },
		[val],
		"<node-url>/"+endpointVal
	);
}


// Validates the authz array common to most LR service descriptions
function validateAuthz(arr) {
	return new FunctionalAssertionResult(
		function(a) { 
			if(a == null || a.length == 0)
				return false;
			return s_is_subset(a, ["none", "basicauth", "oauth", "ssh"]);
		}, 	
		[arr],
		"subset of fixed vocab ['none', 'basicauth', 'oauth', 'ssh']"
	);
}

/* 
	Validates Flow Control.
	In instances where id_limit or doc_limit are asserted
	before flow control has been evaluated as being on or off,
	the evaluation is pushed to the FlowControl object 
	and called here. Any errors with the deferred evaluations
	still trigger a failure and push an error message to the 
	AssertionResults, despite returning true before being evaluated.
*/
function validateFlowControl(controlEnabled) {
	return new FunctionalAssertionResult(
		function(val) {
			if(val && val === true) 
				FlowControl.evaluated = true;  
				
			FlowControl.active = true;
			
			for(var i = 0; i < FlowControl.evals.length; i++)  {
				var currentResult = FlowControl.evals[i]();
				if (!currentResult.passed) {
					failures.push(currentResult.msg);
					testPassed = false;
				}
			}
			return typeof val == "boolean" ;
		},
		[controlEnabled],
		"boolean value"
	);
}

function validateFlowControlLimit(flowLimitVal) {
	function validateLimit(val) {
		
		function evalLimitResult() {
			var resultsObj = {};	
			if(!FlowControl.active) {
				resultsObj.passed = typeof val == "undefined";
				if(!resultsObj.passed) 
					resultsObj.msg = "Flow control is off. Limits should not be present.";
			} else {
				resultsObj.passed = val && val > 0; 
				if(!resultsObj.passed)
					resultsObj.msg = "Invalid limit: "+val+" is not a positive integer.";
			}
			return resultsObj;
		}
		
		if(FlowControl.evaluated) {
	 		var flowEval = evalLimitResult();
	 		if(!flowEval.passed) 
	 			failures.push(resultsObj.msg);
	 		return flowEval.passed;
	 	} else {
	 		FlowControl.evals.push(evalLimitResult);
	 		return true; //possibly refactor error reporting to accomodate to deferred result execution
	 	}
 	}
 	
 	return new FunctionalAssertionResult(validateLimit, [flowLimitVal], "positive integer (or flow control off)");
}

// expected return values from string read from file
eval("var expected ="+ Parameters);

var failures = [];
var flowControlOn = false,
	 flowControlEvaluated = false;
	 
var FlowControl = {
	evaluated: false,
	active: false,
	evals: []
}

//flags
var foundService = false;
var testPassed = true;

//actual values received from the server's response
eval('var json = '+prev.getResponseDataAsString());

try {
	if (json.services) {
		for (i=0; i<json.services.length; i++) {

			var serviceDocument = json.services[i];
			
			var serviceName = serviceDocument["service_name"];
			if (serviceName == expected["service_name"])
			{
				foundService = true;
				assert_r(serviceDocument, expected);
			}			
		}
		if (!testPassed || !foundService)
		{
			var message =  "TEST FAILED\n";
			
			if(!foundService)
				message = "Couldn't find a service named '"+expected["service_name"]+"'";
			else {
				for (var i = 0; i < failures.length; i++)
					message += failures[i];
			}
			raiseError(message);
		}
	} else {
		raiseError( "Bad Reply" );
	}
} catch (error) {
	OUT.println(error);
}


//put in variables
//vars.put("foundService2", foundService);

