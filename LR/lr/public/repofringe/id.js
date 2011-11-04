var doBrowserID = function() {
	navigator.id.getVerifiedEmail(function(assertion) {
		if (assertion) {
			jwt = assertion.split(".");
			var headBytes = Crypto.util.base64ToBytes(jwt[0]);
			var claimBytes = Crypto.util.base64ToBytes(jwt[1]);
			
			var header = Crypto.charenc.Binary.bytesToString(headBytes);
			var claim = Crypto.charenc.Binary.bytesToString(claimBytes);
			
			console.dir({jwt_head: header, jwt_claim: claim});
		} else {
			console.log("not logged in");
		}
		
		verifyAssertion(assertion);
	});
}

var verifyAssertion = function(assertion) {
	if (assertion) {
	    // Now we'll send this assertion over to the verification server for validation
	    // WARNING: This is only an example. In real apps, this verification step must be done from server-side code. 
	    $.ajax({
	      url: 'https://browserid.org/verify',
	      type: 'POST',
	      dataType: "json",
	      data: {
	        audience: window.location.host,
	        assertion: assertion
	      },
	      success: function(data, textStatus, jqXHR) {
	        var l = $("#input .login").removeClass('clickable');
	        l.empty();
	        l.css('opacity', '1');
	        l.append("Yo, ")
	          .append(data.email)
	          .append("!");
	        l.append($('<br/><a href="./" >(logout)</a>'));
	        l.unbind('click');

	        var iurl = 'http://www.gravatar.com/avatar/' +
	          Crypto.MD5($.trim(data.email).toLowerCase()) +
	          "?s=32";
	        $("<img>").attr('src', iurl).appendTo($("#input .picture"));

	        $(".secure").removeClass('secure');
	      },
	      error: function(jqXHR, textStatus, errorThrown) {
	        $("#input .login").css('opacity', '1');
	      }
	    });
	  } else {
	    // something went wrong!  the user isn't logged in.
	    $("#input .login").css('opacity', '1');
	  }
}

jQuery(function() {
	
	$("#input .login").click(doBrowserID).addClass("clickable");
});
