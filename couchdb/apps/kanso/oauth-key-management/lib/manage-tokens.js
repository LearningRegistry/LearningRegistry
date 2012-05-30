
var session = require("session"),
    users = require("users"),
    _ = require("underscore")._;

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
                console.log(err);
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
                            console.log(err);
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

function getUserInfo(email) {
    users.get(email, function(err, doc) {
        if (!err) {
            getOAuth(email, doc);
            getSigningInfo(email, doc);
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


exports.registerCallbacks = function() {
    $.couch.browserid.login(function(evt, err, info) { 
        try {
            if (info && info.email) {
                console.log(info.email);
                getUserInfo(info.email);
            }
        } catch (error) {

        } finally {

        } 
    });

    $.couch.browserid.logout(function(evt, err, info){
        window.location.reload();
    });

    $("#info_update").bind('click', setSigningInfo);
    $("#regenerate").bind('click', revokeAndGenerate);
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

