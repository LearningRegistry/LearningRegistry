import logging, couchdb, oauth2, json, sys
from pylons import config, request as r, response as res, session
from pylons.controllers.util import abort
from functools import wraps

log = logging.getLogger(__name__)

appConfig = config['app_conf']

class Error(RuntimeError):
    """Generic exception class."""

    def __init__(self, message='OAuth error occurred.'):
        self._message = message

    @property
    def message(self):
        """A hack to get around the deprecation errors in 2.6."""
        return self._message

    def __str__(self):
        return self._message

class BadOAuthSignature(Error):
    pass


class OAuthJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (oauth2.Consumer, oauth2.Token)):
            return { "key": o.key, "secret": o.secret }
        return json.JSONEncoder.default(self, obj)


class CouchDBOAuthUtil():
    def __init__(self, couchdb_dba_url=appConfig['couchdb.url.dbadmin'], users_db=appConfig['couchdb.db.users'], oauth_view=appConfig['couchdb.db.users.oauthview']):
            self.server = couchdb.Server(couchdb_dba_url)
            self.users = self.server[users_db]
            self.oauth_view = oauth_view
      

    def find_possible(self, consumer, token, mapper=None):

        def wrap_row(row):
            # log.error("wrap_row: "+json.dumps(row))
            row_result = {}
            if "doc" in row:
                row_result["name"] = row["doc"]["name"]
                row_result["consumer"] = oauth2.Consumer(key=consumer, secret=row["doc"]["oauth"]["consumer_keys"][consumer])
                row_result["token"] = oauth2.Token(key=token, secret=row["doc"]["oauth"]["tokens"][token])
                row_result["id"] = row["doc"]["_id"]
                row_result["roles"] = row["doc"]["roles"]

                if mapper:
                    mapper(row_result, row)

            return row_result

        view_opts = {
            "key":[consumer, token], 
            "include_docs":True
            }

        view_results = self.users.view(self.oauth_view, wrapper=wrap_row, **view_opts)
        return view_results.rows

    def check_request(self, request, mapper=None):

        http_method = request.method
        http_url = request.host_url + request.path_info
        headers = request.headers
        query_string = request.query_string
        info = None
        parameters = None


        oa_request = oauth2.Request.from_request(http_method, http_url, headers, query_string=query_string)
        if oa_request and all([ x in oa_request for x in ['oauth_consumer_key', 'oauth_token']]):
            server = oauth2.Server()
            server.add_signature_method(oauth2.SignatureMethod_HMAC_SHA1())

            
            last_exc = None
            for row in self.find_possible(oa_request['oauth_consumer_key'], oa_request['oauth_token'], mapper):
                try:
                    parameters = server.verify_request(oa_request, row["consumer"], row["token"])
                except oauth2.Error as e:
                    last_exc = BadOAuthSignature("OAuth2 Error: %s" % e.message)
                except:
                    import sys
                    log.exception("Caught Exception in CouchDBOAuthUtil")
                    last_exc = BadOAuthSignature(sys.exc_info()[1])

                if parameters != None:
                    info = row
                    break

            if parameters == None and last_exc != None:
                raise last_exc

        return (parameters, info)

_authobj = CouchDBOAuthUtil()

DEFAULT_SESSION_KEY = "oauth"

class authorize(object):
    Okay = "Okay"
    NoSignature = "No Signature"
    BadSignature = "Bad Signature"
    Error = "Error"
    Unknown = "Unknown"

    def __init__(self, session_key=DEFAULT_SESSION_KEY, roles=None, require=None, mapper=None):
        self.require = require
        self.roles = roles
        self.mapper = mapper
        self.session_key=session_key
    def __call__(self, fn):
        
        @wraps(fn)
        def wrap(*args, **kwargs):
            success = { "status": authorize.Unknown, "user": None, "parameters": None }
            try:
                success["parameters"], success["user"] = _authobj.check_request(r._current_obj(), self.mapper)
                if success["parameters"] is None:
                    success["status"] = authorize.NoSignature
                else:
                    success["status"] = authorize.Okay
            except BadOAuthSignature as e:
                success["status"] = authorize.BadSignature
                success["detail"] = e.message
            except:
                success["status"] = authorize.Error
                success["detail"] = repr(sys.exc_info())
                log.exception("Caught Exception in authorize")

            sess = session._current_obj()
            sess[self.session_key] = success

            # log.error("in wrap:"+repr(sess[self.session_key]))
            cont = True

            if self.roles:
                cont = UserHasRoles(self.session_key, self.roles)
            
            if self.require:
                cont = self.require(cont)

            if cont:
                return fn(*args, **kwargs)
            else:
                log.error("Unauthorized")
                abort(401, "Unauthorized")

        return wrap



def UserHasRoles(session_key, roles=[] ):
    hasRoles = False
    try:
        s = session._current_obj()
        hasRoles = all([role in s[session_key]["user"]["roles"] for role in roles])
    except:
        pass
    return hasRoles









