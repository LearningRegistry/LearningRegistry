import logging, browserid, json, sys

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import rest

from lr.lib.base import BaseController, render
import lr.lib.oauth as oauth


log = logging.getLogger(__name__)

appConfig = config['app_conf']

def lrsignature_mapper(row_result, row):
    if "lrsignature" in row["doc"]:
        row_result["lrsignature"] = row["doc"]["lrsignature"]
    else:
        row_result["lrsignature"] = { }


class OauthController(BaseController):



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

    
    def verify(self):
        
        # from pprint import pformat
        values = ""
        for key in dir(request):
            if hasattr(request, key):
                try:
                    values += "%s : %s\n" % (key, getattr(request,key))
                except:
                    values += "%s : %s\n" % (key, "ERROR")
                    pass
        log.error(values)

        # util = oauth.CouchDBOAuthUtil()
        # success = {}
        # try:
        #     success["parameters"], user = util.check_request(request)
        #     if success["parameters"] is None:
        #         success["status"] = ["No Signature"]
        #     else:
        #         success["status"] = ["Okay"]
        # except oauth.BadOAuthSignature as e:
        #     success["status"] = ["Bad Signature", e.message]
        # except:
        #     log.exception("Caught Exception in verify")
        from beaker.session import Session as BeakerSession
        real_session = session._current_obj()
        params = real_session.__dict__['_params']
        real_session.__dict__['_sess'] = BeakerSession({}, **params)

        session["foo"] = {}
        @oauth.authorize(session["foo"], roles=None, require=None, mapper=lrsignature_mapper)
        def doVerify():
            success = session["foo"]
            log.error(repr(success))
            return repr(success)

        return doVerify()
        

    def login(self):
        data = None
        if request.method == 'POST' and "assertion" in request.POST:
            data = browserid.verify(request.POST["assertion"], request.host_url)
            log.debug(json.dumps(data))

        if data['status'] == 'okay':
            session['contact'] = data['email']
            session.save()   

        return json.dumps(data)

    def logout(self):
        session.clear()
        session.save()
        return json.dumps({"status": "okay"})
        

    def manage(self):
        for i in request.POST.keys():
            log.debug("{0} : {1}".format(i, request.POST[i]))

        if 'contact' in session:
            log.debug(session['contact'])

        return 




