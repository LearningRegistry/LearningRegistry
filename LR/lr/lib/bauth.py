from decorator import decorator
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
        try:
            h = {}
            h.update(json_header)
            h.update(auth_header)
            req = urllib2.Request(self.session_url, headers=h)
            res = urllib2.urlopen(req)
            j_res = json.load(res)
            user = None
            if "userCtx" in j_res and "name" in j_res["userCtx"] and j_res["userCtx"]["name"] is not None:
                user = j_res["userCtx"]
            return user
        except Exception as ex:
            log.error(ex)
            abort(401, "Basic Authorization Required", headers=h)

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

class status(object):
    Okay = "Okay"
    NotAuthorized = "NotAuthorized"

def authorize(session_key="validate-basic", service_doc=None, roles=None, realm=None, pre_cond=None, post_cond=None):
    _session_key = session_key
    _roles = roles
    _post_cond = post_cond
    _pre_cond = pre_cond
    _realm = realm or ""
    _service_doc = service_doc

    def wrapper(fn, self, *args, **kwargs):

        if _service_doc:
            sdoc = _service_doc()
            try:
                if "basicauth" not in sdoc["service_auth"]["service_authz"]:
                    return fn(self, *args, **kwargs)
            except:
                raise ValueError("Missing service_document for checking if OAUTH access is enabled.")

        if _pre_cond:
            precond = _pre_cond()
        else:
            precond = True

        # if precondition is true, continue with auth. otherwise skip
        if precond:    
            sess = session._current_obj()

            success = {}
            success["user"], success["status"] = _authUtil.validate_session(_roles)
            sess[_session_key] = success

            # log.error("in wrap:"+repr(sess[_session_key]))
            cont = success["status"] and success["user"]
            if cont:
                success["status"] = status.Okay
            else:
                success["status"] = status.NotAuthorized

            if _post_cond:
                cont = _post_cond(cont)
        else:
            cont = True

        if cont:
            return fn(self, *args, **kwargs)
        else:
            h = {"WWW-Authenticate": "Basic realm=\"{0}\"".format(_realm)}
            log.error("Authorization Required")
            response.headers.update(h)
            abort(401, "Basic Authorization Required", headers=h)

    return decorator(wrapper)


