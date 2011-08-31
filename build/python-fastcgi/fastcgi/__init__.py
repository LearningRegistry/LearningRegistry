"""
Python bindings for the Open Market FastCGI library
"""

__author__  = "Cody Pisto <cody@hpcs.com>"
__version__ = "1.0"

from Server import ThreadedServer, ForkingServer
from WSGI import ThreadedWSGIServer, ForkingWSGIServer
