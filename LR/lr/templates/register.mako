<html>
	<head>
		<title>Register for Distribute</title>


        <style type="text/css">
            div.form {
                display: none;
                width: 400px;
            }

            div.form label {
                display: block;
            }

            div.form input {
                display: block;
                width: 100%;
            }

            .error {
                color: #f00;
            }

        </style>
	</head>
    <body>
    <h1>Register for Distribute</h1>
    <div class="login">
        <p>Please Sign-in with BrowserID to create a distribution link.</p>
        <a href="#" id="browserid" title="Sign-in with BrowserID">  
          <img src="/images/sign_in_blue.png" alt="Sign in">  
        </a>
    </div>
    <div class="msg"></div>
    <div class="form">
            <label for="contact">Contact Email:</label>
            <input type="text" id="contact" name="contact" disabled="disabled">

            <label for="destUrl">Destination URL:</label>
            <input type="text" id="destUrl" name="destUrl"/>

            <label for="username">Username:</label>
            <input type="text" id="username" name="username"/>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password"/>
            <button id="register">Register</button>
    </div>
	
	</body>
</html>
<script src="https://browserid.org/include.js" type="text/javascript"></script>
<script src="/script/require-jquery.js" data-main="script/distribute" type="text/javascript"></script>