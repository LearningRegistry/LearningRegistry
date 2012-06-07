from pylons import config, request, session, response
from pylons.controllers.util import abort
from functools import wraps
import urllib2, couchdb, logging, json

log = logging.getLogger(__name__)

appConfig = config['app_conf']
json_header = { 'Content-type': 'application/json; charset=utf-8'}
class CouchDBBasicAuthUtil(object):
    def __init__(self, couchdb_url=appConfig['couchdb.url'], users_db=appConfig['couchdb.db.users']):
            self.couchdb_url = couchdb_url
            self.users_db = users_db

            self.session_url = "{0}/_session".format(couchdb_url)
            self.users_url = "{0}/{1}/org.couchdb.user:".format(couchdb_url, users_db)

    def _get_user_from_session(self, auth_header):
        h = {}
        h.update(json_header)
        h.update(auth_header)
        log.error("headers: "+json.dumps(h))
        req = urllib2.Request(self.session_url, headers=h)
        res = urllib2.urlopen(req)
        j_res = json.load(res)
        log.error("j_res: "+json.dumps(j_res))
        user = None
        if "userCtx" in j_res and "name" in j_res["userCtx"] and j_res["userCtx"]["name"] is not None:
            user = j_res["userCtx"]
        return user

    def _check_user_has_roles(self, user, roles=None):
        hasRoles = True
        if user and roles and len(roles) > 0:
            try:
                hasRoles = all([role in u["roles"] for role in roles])
            except:
                pass
        elif not user and roles:
            hasRoles = False

        return hasRoles

    def validate_session(self, roles=None):
        req = request._current_obj()
        user = None
        if req.authorization and req.authorization[0] == "Basic":
            user = self._get_user_from_session({"Authorization": "{0} {1}".format(*req.authorization)})

        return (user, self._check_user_has_roles(user, roles))


_authUtil = CouchDBBasicAuthUtil()

class authorize(object):
    Okay = "Okay"
    NotAuthorized = "NotAuthorized"

    def __init__(self, session_key="validate-basic", roles=None, realm=None, pre_cond=None, post_cond=None):
        self.session_key = session_key
        self.roles = roles
        self.post_cond = post_cond
        self.pre_cond = pre_cond
        self.realm = realm or ""

    def __call__(self, fn):
        @wraps(fn)
        def wrap(*args, **kwargs):
            if self.pre_cond:
                precond = self.pre_cond()
            else:
                precond = True

            # if precondition is true, continue with auth. otherwise skip
            if precond:    
                sess = session._current_obj()

                success = {}
                success["user"], success["status"] = _authUtil.validate_session(self.roles)
                sess[self.session_key] = success

                # log.error("in wrap:"+repr(sess[self.session_key]))
                cont = success["status"] and success["user"]
                if cont:
                    success["status"] = authorize.Okay
                else:
                    success["status"] = authorize.NotAuthorized

                if self.post_cond:
                    cont = self.post_cond(cont)
            else:
                cont = True

            if cont:
                return fn(*args, **kwargs)
            else:
                h = {"WWW-Authenticate": "Basic realm=\"{0}\"".format(self.realm)}
                log.error("Authorization Required")
                response.headers.update(h)
                abort(401, "Authorization Required", headers=h)

        return wrap


