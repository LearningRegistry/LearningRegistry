import logging, couchdb, oauth2, json, sys
from decorator import decorator
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
        elif isinstance(o, Exception):
            return { 
                "type": type(o).__name__,
                "message": o.message }
        try:
            return json.JSONEncoder.default(self, o)
        except Exception as e: 
            log.exception("Encoded Type: {0}\nrepr: {1}".format(type(o), repr(o)))
            raise e


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

        # log.error("*** CHECK_REQUEST *** "+json.dumps({
        #     "query_string": query_string,
        #     "headers": {}.update(headers),
        #     "http_method": http_method,
        #     "http_url": http_url
        #     }))
        

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

class status(object):
    Okay = "Okay"
    NoSignature = "No Signature"
    BadSignature = "Bad Signature"
    Error = "Error"
    Unknown = "Unknown"

def authorize(session_key=DEFAULT_SESSION_KEY, service_doc=None, roles=None, mapper=None, realm=None, pre_cond=None, post_cond=None):
    
    _roles = roles
    _mapper = mapper
    _session_key=session_key
    _realm = realm or ""
    _pre_cond = pre_cond
    _post_cond = post_cond
    _service_doc = service_doc

    def wrapper(fn, self, *args, **kwargs):
        if _service_doc:
            sdoc = _service_doc()
            try:
                if "oauth" not in sdoc["service_auth"]["service_authz"]:
                    return fn(self, *args, **kwargs)
            except:
                raise ValueError("Missing service_document for checking if OAUTH access is enabled.")

        if _pre_cond:
            precond = cont = _pre_cond()
        else:
            precond = cont = True

        if precond:
            success = { "status": status.Unknown, "user": None, "parameters": None }
            try:
                success["parameters"], success["user"] = _authobj.check_request(r._current_obj(), _mapper)
                if success["parameters"] is None:
                    success["status"] = status.NoSignature
                else:
                    success["status"] = status.Okay
            except BadOAuthSignature as e:
                success["status"] = status.BadSignature
                success["detail"] = e.message
                cont = False
            except:
                success["status"] = status.Error
                success["detail"] = repr(sys.exc_info())
                log.exception("Caught Exception in authorize")
                cont = False

            sess = session._current_obj()
            sess[_session_key] = success

            # log.error("in wrap:"+repr(sess[_session_key]))
            
            if cont and _roles:
                cont = UserHasRoles(_session_key, _roles)
        
            if _post_cond:
                cont = _post_cond(cont)


        if cont:
            try:
                return fn(self, *args, **kwargs)
            finally:
                pass
        else:
            h = {"WWW-Authenticate": "OAuth realm=\"{0}\"".format(_realm)}
            log.error("Authorization Required")
            res.headers.update(h)
            abort(401, "OAuth Authorization Required", headers=h)

    return decorator(wrapper)



def UserHasRoles(session_key, roles=[] ):
    hasRoles = False
    try:
        s = session._current_obj()
        hasRoles = all([role in s[session_key]["user"]["roles"] for role in roles])
    except:
        pass
    return hasRoles









