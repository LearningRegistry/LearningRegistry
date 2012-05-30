import logging, browserid, json

from pylons import config, request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

appConfig = config['app_conf']

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

        pass

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




