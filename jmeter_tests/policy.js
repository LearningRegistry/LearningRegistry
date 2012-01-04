// expected return values from string read from file
eval("var expected ="+ Parameters);

var failures = [];

//flags
var foundService = false;
var testPassed = true;

//actual values received from the server's response
eval('var result = '+prev.getResponseDataAsString());

if (result.doc_type == "policy_description") {
	assert_r(result, expected, false);
	if (!testPassed) {
		var message =  "TEST FAILED\n";
		for (var i = 0; i < failures.length; i++)
			message += failures[i];
				
		raiseError(message);
	}
} else {
	raiseError( "Bad Reply" );
}
