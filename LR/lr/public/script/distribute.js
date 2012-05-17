require(["jquery"], function($) {
    $(function() {
        $('#browserid').click(function() {
            navigator.id.get(gotAssertion);
            return false;
        });
    });


    function loggedIn(emailAddress) {
        $("div.login").hide();

        $("#contact").val(emailAddress);
        $("#register").click(function() {
            

            $.ajax({
                type: 'POST',
                url: '/register/create',
                data: {
                    contact: emailAddress,
                    destUrl: $('#destUrl').val(),
                    username: $('#username').val(),
                    password: $('#password').val()
                },
                success: function(res, status, xhr) {
                    $("div.msg").empty();

                    if (res.status === "okay") {
                        $("div.form").hide();
                        cls = '';
                    } else {
                        cls = ' class="error"';
                    }

                    if (res.msg) {
                        $("<p"+cls+"/>").text(res.msg).appendTo($("div.msg"));
                    }
                    if (res.message) {
                        $("<p"+cls+"/>").text(res.message).appendTo($("div.msg"));
                    }

                },
                error: function(res, status, xhr) {

                    $("div.msg").empty();

                    if (res.msg) {
                        $('<p class="error" />').text(res.msg).appendTo($("div.msg"));
                    }
                    if (res.message) {
                        $('<p class="error" />').text(res.message).appendTo($("div.msg"));
                    }
                    if (res.responseText) {
                        msg = "An Unknown error occurred.";
                        try {
                            msg = JSON.parse(res.responseText).message;
                        } catch (error) {
                            msg = res.responseText;
                        }

                         $('<p class="error" />').text(msg).appendTo($("div.msg"));
                    }

                }
            });

        });

        $("div.form").show();



    }

    function gotAssertion(assertion) {  
        // got an assertion, now send it up to the server for verification  
        if (assertion !== null) {  
            $.ajax({  
                type: 'POST',  
                url: '/register/verify',  
                data: { assertion: assertion },  
                success: function(res, status, xhr) {  
                    if (res === null) {}//loggedOut();  
                    else {
                        loggedIn(res.email);
                     //loggedIn();
                    };  
                },  
                error: function(res, status, xhr) {  
                    alert("login failure:" + JSON.stringify(res));  
                }  
            });  
        } else {  

            $("<h1>Logged Out</h1>").appendTo($("div.msg"));
            //loggedOut();  
        }  
    }

});