/* utils.js
  Utility functions for validating returned JSON documents.
  
  Austin Montoya
  25 November 2011
*/

/* Builds a primitive object that can be returned
   from assertion functions for more detailed/accurate 
   error messages.
   
   While function invocation is not necessary to 
   generate our desired object, it gives us a 
   reference to the caller that may be used
   for debugging purposes (stack trace, etc).
*/
function FunctionalAssertionResult(fn, vals, errVal) {
	this.func = fn;
	this.success = this.func.apply(this, vals);
	this.msg = (this.success) ? "success" : errVal;
	return this;
}

// Douglas Crockford's improved typeof function.
function typeOf(value) {
    var s = typeof value;
    if (s === 'object') {
        if (value) {
            if (typeof value.length === 'number' &&
                    !(value.propertyIsEnumerable('length')) &&
                    typeof value.splice === 'function') {
                s = 'array';
            }
        } else {
            s = 'null';
        }
    }
    return s;
};

// Ensures that the value is either undefined or a type
function isTypeOrUndefined(val, type) {
	function typeOrUndef(v,t) {
		var actualType = typeOf(v);
		return actualType == "undefined" || actualType == t;	
	}
	
	return new FunctionalAssertionResult(typeOrUndef, [val,type], 
													"an object of type "+type+" or undefined");
}

// Checks that a value is a string and that the string is not empty
function isNonEmptyString(val) { 
	return new FunctionalAssertionResult(
		function(v) { return v != null && typeof v == "string"; },
		[val],
		"non-null string"
	)
}

// Ensures that the version number is equivalent
// i.e. "0.21.0" being the same as "0.21"
function isMatchingVersion(received, expected) {
	function matchingVersion(val, exp) {
		if(val && exp.length != val.length ) {
			var shorter = (exp.length > val.length ) ? val : exp,
				 longer  = (shorter == exp) ? val : exp,
				 rest    = longer.substr(shorter.length, longer.length - 1);
			
			for(var i = 0; i < rest.length; i++) {
				if((rest[i] != '0' && rest[i] != '.')
					|| (i > 0 && rest[i] == '.' && rest[i-1] == '.')) //no double dots!
					return false;
				else
					continue;
			}
			return true;
		} else 
			return val === exp;
	}
	
	return new FunctionalAssertionResult(matchingVersion, [received,expected], expected);
}

// Notifies the AssertionListener that the test has failed for
//	one or more reasons (txt contains error string to write to file)
function raiseError(txt) {
	AssertionResult.setFailureMessage(txt);
	AssertionResult.setFailure(true);
};

// Iterates through obj's keys and validates
// that they also exist in exp
function detect_extra_keys(obj, exp) {
	for(prop in obj)
		if(typeof exp[prop] == "undefined") {
			testPassed = false;
			failures.push("Key '"+prop+"' is not defined in the expected object\n");
		}	
}


// Compares two arrays of strings, validating
// that the first array is a subset of the second
function s_is_subset(arr1, arr2) {
	for(var i =0; i < arr1.length; i++) {
		
		//Check for repeated elements
		var item = arr1[i];
		for(var j = 0; j < arr1.length; j++) {
			if(j == i)
				continue;
			else if (arr1[j] == item)
				return false;
		}
		
	 	if(arr2.indexOf(item) == -1)
	 		return false;
   }
   return true;
}

/* Validates that the properties of the second
	object equal those of the first.
	
	Will recursively visit objects and arrays.
	
	If a function is mapped to a property of the second object,
	it will evaluate the value of the first object's corresponding 
	property using that function.
	
	Also checks for extra keys in the first object.
*/
function assert_r(obj, exp, detectExtraKeys) {
	if(detectExtraKeys)
		detect_extra_keys(obj, exp);
	for (var prop in exp)
		if ( typeOf(exp[prop]) == "object" )
			assert_r(obj[prop], exp[prop], detectExtraKeys);
		else {
			var passed = false;
			var funResult = null;
			
			if ( typeOf(exp[prop]) == "function" ) { 
				/* If exp[prop] is a function, then get the object
					returned from that function. */
				funResult = exp[prop](obj[prop]);
				passed = funResult.success;
		   } else if ( typeOf(exp[prop]) == "array" ) {
		   	/* If exp[prop] is an array, then assert each object in that array
		   		TODO: Make it work for arrays that contain primitive values (none currently defined in spec) */
				for(var i = 0; i < exp[prop].length; i++) 
					assert_r(obj[prop][i], exp[prop][i], detectExtraKeys);
				passed = true;
			} else 
				passed = obj[prop] == exp[prop];					
			if(!passed) {
				testPassed = false;
				var expectedVal = (funResult) ? funResult.msg : exp[prop];
				failures.push("\t\t"+prop + ": Expected " +expectedVal+ ", got " +obj[prop]+ "\n");
			}
		}
}