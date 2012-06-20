exports.validate_doc_update = 
    function(newDoc, oldDoc, userCtx, secObj) {
        if (newDoc._deleted === true) {
            // allow deletes by admins and matching users
            // without checking the other fields
            if ((userCtx.roles.indexOf('_admin') !== -1) ||
                (userCtx.name == oldDoc.name)) {
                return;
            } else {
                throw({forbidden: 'Only admins may delete other user docs.'});
            }
        }


        var is_server_or_database_admin = function(userCtx, secObj) {
            // see if the user is a server admin
            if(userCtx.roles.indexOf('_admin') !== -1) {
                return true; // a server admin
            }

            // see if the user a database admin specified by name
            if(secObj && secObj.admins && secObj.admins.names) {
                if(secObj.admins.names.indexOf(userCtx.name) !== -1) {
                    return true; // database admin
                }
            }

            // see if the user a database admin specified by role
            if(secObj && secObj.admins && secObj.admins.roles) {
                var db_roles = secObj.admins.roles;
                for(var idx = 0; idx < userCtx.roles.length; idx++) {
                    var user_role = userCtx.roles[idx];
                    if(db_roles.indexOf(user_role) !== -1) {
                        return true; // role matches!
                    }
                }
            }

            return false; // default to no admin
        }

        if (!is_server_or_database_admin(userCtx, secObj)) {
            if (newDoc) {
                throw({
                    forbidden: 'Only server or db admin can modify this db.'
                });
            }
        }

        

    }
