import logging, browserid, json, sys

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest

from lr.lib.base import BaseController, render
from lr.lib import oauth, bauth
from lr.lib.signing import lrsignature_mapper

# import rpdb2; rpdb2.start_embedded_debugger("password")

log = logging.getLogger(__name__)

appConfig = config['app_conf']

def continue_if_missing_oauth():
    try:
        log.error("continue_if_missing_oauth"+repr(session["prefer-verify"]))
        nosig = (session["prefer-verify"]["status"] == oauth.status.NoSignature)
        if nosig:
            session["prefer-verify"] = None
        return nosig
    except:
        return True

def never_abort(*vars):
    return True




class AuthController(BaseController):



    def index(self):
        response.headers['Content-Type'] = 'text/html;charset=utf-8'
        # Return a rendered template
        response.status_int = 301
        response.headers['Location'] = appConfig['lr.oauth.signup']
        return "Moved: %s" % appConfig['lr.oauth.signup']
        # return render('/oauth.html')
        # or, return a string
        # return 'Hello World'
        # response.headers['Pragma'] = 'no-cache'
        # response.headers['Cache-Control'] = 'no-store,no-cache,must-revalidate,max-age=0'
        # return abort(301, detail=appConfig['lr.oauth.signup'])
        
        # return "Moved permanently: %s" % appConfig['lr.oauth.signup']

    @oauth.authorize("oauth-verify", roles=None, mapper=lrsignature_mapper, post_cond=never_abort)
    def oauth_verify(self, *args, **kwargs):
        # from pprint import pformat
        # values = ""
        # for key in dir(request):
        #     if hasattr(request, key):
        #         try:
        #             values += "%s : %s\n" % (key, getattr(request,key))
        #         except:
        #             values += "%s : %s\n" % (key, "ERROR")
        #             pass
        # log.error(values)
        
        success = session["oauth-verify"]
        return json.dumps(success, cls=oauth.OAuthJSONEncoder)

    @bauth.authorize("basic-verify", roles=None, pre_cond=None, realm="Learning Registry")
    def basic_verify(self, *args, **kwargs):
        # from pprint import pformat
        # values = ""
        # for key in dir(request):
        #     if hasattr(request, key):
        #         try:
        #             values += "%s : %s\n" % (key, getattr(request,key))
        #         except:
        #             values += "%s : %s\n" % (key, "ERROR")
        #             pass
        # log.error(values)
        
        success = session["basic-verify"]
        return json.dumps(success, cls=oauth.OAuthJSONEncoder)

    @oauth.authorize("prefer-verify", roles=None, mapper=lrsignature_mapper)
    @bauth.authorize("prefer-verify", roles=None, pre_cond=continue_if_missing_oauth, realm="Learning Registry")
    def prefer_oauth_basic(self, *args, **kwargs):
        # from pprint import pformat
        # values = ""
        # for key in dir(request):
        #     if hasattr(request, key):
        #         try:
        #             values += "%s : %s\n" % (key, getattr(request,key))
        #         except:
        #             values += "%s : %s\n" % (key, "ERROR")
        #             pass
        # log.error(values)
        
        success = session["prefer-verify"]
        return json.dumps(success, cls=oauth.OAuthJSONEncoder)


    # def login(self):
    #     data = None
    #     if request.method == 'POST' and "assertion" in request.POST:
    #         data = browserid.verify(request.POST["assertion"], request.host_url)
    #         log.debug(json.dumps(data))

    #     if data['status'] == 'okay':
    #         session['contact'] = data['email']
    #         session.save()   

    #     return json.dumps(data)

    # def logout(self):
    #     session.clear()
    #     session.save()
    #     return json.dumps({"status": "okay"})
        

    # def manage(self):
    #     for i in request.POST.keys():
    #         log.debug("{0} : {1}".format(i, request.POST[i]))

    #     if 'contact' in session:
    #         log.debug(session['contact'])

    #     return 




