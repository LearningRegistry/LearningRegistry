from Server import ThreadedServer, ForkingServer
import traceback


class WSGIMixIn:
    def handle(self, req):
        environ = req.environ
        environ['wsgi.input']        = req.stdin
        environ['wsgi.errors']       = req.stderr
        environ.update(self._environ)

        if environ.get('HTTPS','off') in ('on','1'):
            environ['wsgi.url_scheme'] = 'https'
        else:
            environ['wsgi.url_scheme'] = 'http'

        headers_set = []
        headers_sent = []

        def write(data):
            if not headers_set:
                raise AssertionError("write() before start_response()")

            elif not headers_sent:
                # Before the first output, send the stored headers
                status, response_headers = headers_sent[:] = headers_set
                req.stdout.write('Status: %s\r\n' % status)
                for header in response_headers:
                    req.stdout.write('%s: %s\r\n' % header)
                req.stdout.write('\r\n')

            req.stdout.write(data)
            req.stdout.flush()

        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    if headers_sent:
                        # Re-raise original exception if headers sent
                        raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None     # avoid dangling circular ref
            elif headers_set:
                raise AssertionError("Headers already set!")
            
            headers_set[:] = [status,response_headers]
            return write

        result = self._app(environ, start_response)
        try:
            for data in result:
                if data:    # don't send headers until body appears
                    write(data)
            if not headers_sent:
                write('')   # send headers now if body was empty
        finally:
            if hasattr(result,'close'):
                result.close() 

    def error(self, req, e):
        traceback.print_exc(file=req.stderr)
        req.stderr.flush()


class ThreadedWSGIServer(WSGIMixIn, ThreadedServer):

    _environ = { 'wsgi.version':      (1,0),
                 'wsgi.multithread':  True,
                 'wsgi.multiprocess': True,
                 'wsgi.run_once':     False }

    def __init__(self, app, workers=5):
        ThreadedServer.__init__(self, workers)

        self._app = app


class ForkingWSGIServer(WSGIMixIn, ForkingServer):

    _environ = { 'wsgi.version':      (1,0),
                 'wsgi.multithread':  False,
                 'wsgi.multiprocess': True,
                 'wsgi.run_once':     False }

    def __init__(self, app, workers=5):
        ForkingServer.__init__(self, workers)

        self._app = app

