import fcgi
import threading
import os
import sys


class Server:
    def __init__(self, workers=5):
        self._workers = workers 

    def _mainloop(self):
        req = fcgi.Request()

        while True:
            try:
                req.accept()
            except:
                break

            try: 
                self.handle(req)
            except Exception, e:
                self.error(req, e)

    def error(self, req, e):
        """Override me"""
        raise NotImplementedError

    def handle(self, req):
        """Override me"""
        raise NotImplementedError

    def serve_forever(self):
        """Override me"""
        raise NotImplementedError


class ThreadedMixIn:
    def serve_forever(self):

        for x in range(self._workers - 1):
            t = threading.Thread(target=self._mainloop)
            t.start()

        self._mainloop()


class ForkingMixIn:
    def serve_forever(self):

        for x in range(self._workers - 1):
            pid = os.fork()
            if not pid:
                # child
                self._mainloop()
                sys.exit(0)
            else:
                # parent
                continue

        self._mainloop()


class ThreadedServer(ThreadedMixIn, Server): pass
class ForkingServer(ForkingMixIn, Server): pass

