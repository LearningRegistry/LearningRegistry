#!/usr/bin/env python

import fastcgi

def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']

#s = fastcgi.ForkingWSGIServer(simple_app, workers=5)
s = fastcgi.ThreadedWSGIServer(simple_app, workers=5)
s.serve_forever()
