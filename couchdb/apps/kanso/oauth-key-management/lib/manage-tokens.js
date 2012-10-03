
var session = require("session"),
    users = require("users"),
    _ = require("underscore")._;

function log(msg) {
    try{
        console.log(msg)
    } catch (e) {

    }
}


function getOAuth(email, doc, regenerate) {
    if (regenerate || !(doc.oauth 
        && doc.oauth.consumer_keys 
        && doc.oauth.consumer_keys[email]
        && doc.oauth.tokens
        && doc.oauth.tokens.node_sign_token)) {

        doc.oauth = doc.oauth || {};
        doc.oauth.consumer_keys = doc.oauth.consumer_keys || {};
        doc.oauth.tokens = doc.oauth.tokens || {};

        doc.oauth.consumer_keys[email] = exports.generateSecret(32);
        doc.oauth.tokens.node_sign_token = exports.generateSecret(32);

        if (!doc.roles || _.indexOf(doc.roles, "node_sign") == -1) {
            doc.roles = doc.roles || [];
            // doc.roles.push("node_sign");
        }

        users.update(email, null, doc, function(err) {
            if (err) {
                log(err);
            } else {
                getUserInfo(email);
            }
        });

    } else {
        $(".oauth").show(500);
        $("#consumer_key").val(email)
        $("#consumer_secret").val(doc.oauth.consumer_keys[email]);
        $("#token_secret").val(doc.oauth.tokens.node_sign_token);
    }
}

function getSigningInfo(email, doc) {
    if (doc.lrsignature && doc.lrsignature.full_name) {
        $("#full_name").val(doc.lrsignature.full_name);
    }
}

function setMessage(msg, wait, cb) {
    if (!wait) {
        wait = 10000;
    }

    $(".msg").fadeOut('fast').empty().text(msg).fadeIn('fast').delay(wait).fadeOut('slow').hide('fast');

    if (cb) {
        cb();
    }
}

function resetForms() {
    $(".oauth").hide(500);
    $("#password").val("");
    $("#verify_password").val("");
    $("#password_set").prop("checked", false);
    $("#consumer_key").val("");
    $("#consumer_secret").val("");
    $("#token_secret").val("");
    $("#full_name").val("");
}

function setSigningInfo() {
    full_name = $("#full_name").val();
    if ($.trim(full_name) !== "") {
        session.info(function(err, session_info){
            if (session_info.userCtx.name) {
                users.get(session_info.userCtx.name, function(err, doc){
                    doc.lrsignature = doc.lrsignature || {}
                    doc.lrsignature.full_name = full_name;

                    users.update(session_info.userCtx.name, null, doc, function(err) {
                        if (err) {
                            log(err);
                            setMessage("Unable to save signing information.");
                        } else {
                            setMessage("Information saved.")
                        }
                    });
                }); 
            };
        });
    }
}

function setPasswordInfo(email, doc) {
    if (doc.password_sha) {
        $("#password_set").prop("checked", true);
    } else {
        $("#password_set").prop("checked", false);
    }
}

function getUserInfo(email) {
    users.get(email, function(err, doc) {
        if (!err) {
            getOAuth(email, doc);
            getSigningInfo(email, doc);
            setPasswordInfo(email, doc);
        }
        else {
            setMessage(err);
        }
    });
}

function revokeAndGenerate() {
    session.info(function(err, session_info){
        if (session_info.userCtx.name) {
            users.get(session_info.userCtx.name, function (err, doc){
                if (!err) {
                   getOAuth(session_info.userCtx.name, doc, true); 
                }
            });
        } else {
            sessionTimeout();
        }
    });
}

function sessionTimeout () {
    setMessage("Session has timed out.", 50000, function(){
        window.location.reload();
    });
}

function checkPasswordMatch() {
    var passwd1 = $("#password").val();
    var passwd2 = $("#verify_password").val();
    if (passwd1 === "" || passwd2 === "" || passwd1 !== passwd2)
        return false;
    return true;
}

function savePassword() {
    var passwd1 = $("#password").val();
    var passwd2 = $("#verify_password").val();
    if ( checkPasswordMatch() ) {
        session.info(function(err, session_info) {
            if (session_info.userCtx.name) {
                users.get(session_info.userCtx.name, function(err, doc){
                    doc.password = passwd1;

                    users.update(session_info.userCtx.name, null, doc, function(err) {
                        if (err) {
                            log(err);
                            setMessage("Unable to save publish password.");
                        } else {
                            setMessage("Password saved.");
                            $("#password").val("");
                            $("#verify_password").val("");
                            $("#password_set").prop("checked", true);
                        }
                    });
                }); 
            };
        });
    } else {
        setMessage("Passwords do no match.");
    }
}


exports.registerCallbacks = function() {
    $.couch.browserid.login(function(evt, err, info) { 
        try {
            var email = null;
            if (info && info.name) {
                email = info.name;
            } else if (info && info.email) {
                email = info.email
            }

            if (email) {
                log(email);
                getUserInfo(email);
            }
        } catch (error) {

        } finally {

        } 
    });

    $.couch.browserid.logout(function(evt, err, info){
        resetForms();
    });

    $("#info_update").bind('click', setSigningInfo);
    $("#regenerate").bind('click', revokeAndGenerate);
    $("#save_password").bind('click', savePassword);
}


// Simple secret key generator
exports.generateSecret = function(length) {
    var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    var secret = '';
    for (var i = 0; i < length; i++) {
        secret += tab.charAt(Math.floor(Math.random() * 64));
    }
    return secret;
}

