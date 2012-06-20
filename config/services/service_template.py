
import abc
import pystache
import types
import urlparse
import pprint
from setup_utils import  PublishDoc
from couch_utils import pushCouchApp
import uuid
import json
from os import path
from urlparse import urljoin, urlsplit, urlunsplit

_COUCHAPP_PATH = path.abspath(path.join(path.dirname(path.abspath(__file__)), '..', '..', 'couchdb'))

def getCouchAppPath():
    return _COUCHAPP_PATH

class ServiceTemplate():
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self.template = '''{
                "doc_type": "service_description",
                "doc_version": "0.20.0",
                "doc_scope": "{{scope}}",
                "active": {{active}},
                "service_id": "{{service_id}}",
                "service_type": "{{service_type}}",
                "service_name": "{{service_name}}",        
                "service_version": "{{service_version}}",
                "service_endpoint": "{{node_endpoint}}{{service_endpoint}}",
                "service_auth": {
                    "service_authz":    [
                        {{service_authz}}
                    ],
                    "service_key": {{service_key}},
                    "service_https": {{service_https}}
                }{{#service_data}},"service_data":{{service_data}}{{/service_data}}
            }'''
        self.couchapps = {}
        self.service_data_template = None
        self.authz_data_template = '''{{authz}}'''
        self.opts = {
            "scope": "node",
            "active": "false",
            "service_id": None,
            "service_type": None,
            "service_name": None,
            "service_version": None,
            "node_endpoint": None,
            "service_endpoint": None,
            "authz": ["none"],
            "service_authz": self._authz,
            "service_key": "false", 
            "service_https": "false",
            "service_data": self._servicedata
        }

    def _optsoverride(self):
        return {}
  
    def _servicedata(self, **kwargs):
        if self.service_data_template != None:
            return pystache.render(self.service_data_template, kwargs)
        return None
        
    def _authz(self, **kwargs):
        if self.authz_data_template != None:
            if 'authz' in kwargs and isinstance(kwargs['authz'], types.ListType):
                kwargs['authz'] = ','.join(map(lambda x: '"%s"' % x, kwargs['authz']))
            
            return pystache.render(self.authz_data_template, kwargs)
        return None
        
    def _getId(self):
        return "{0}:{1} service".format(self.opts['service_type'], self.opts['service_name'])

    def install(self, server, dbname, customOpts):
        
        config_doc = self.render(**customOpts)
        doc = json.loads(config_doc)
        
        PublishDoc(server, dbname, self._getId(), doc)
    
        print("Configured {0} :\n{1}\n".format(self.opts['service_name'],
                                                json.dumps(doc, indent=4, sort_keys=True)))

        self._installCouchApps(_COUCHAPP_PATH, server)
        return self

    def _installCouchApps(self, couchappsDir, server):
        if (self.opts['active'] ==False) or (len(self.couchapps) == 0):
            return

        for db in self.couchapps.keys():
            for app in  self.couchapps[db]:
                appPath = path.abspath(path.join(path.join(couchappsDir, db), app))
                
                if server.resource.credentials:
                    username, password = server.resource.credentials
                    parts = list(urlsplit(server.resource.url))
                    parts[1] = "%s:%s@%s" % (username, password, parts[1])
                    server_url = urlunsplit(parts)
                else:
                    server_url = server.resource.url

                dbUrl =  urljoin(server_url, db)
                
                pushCouchApp(appPath, dbUrl)
                #print("\nPushed couch app {0} to {1}".format(appPath, dbUrl))
                

    def render(self, **kwargs):
        self.opts.update(self._optsoverride())

        funcs = []
        for key in self.opts.keys():
            if key in kwargs:
                if isinstance(kwargs[key], types.BooleanType):
                    self.opts[key] = repr(kwargs[key]).lower()
                else:
                    self.opts[key] = kwargs[key]
                
            if isinstance(self.opts[key], (types.FunctionType, types.MethodType) ):
                funcs.append(key)
    
        for key in funcs:
            self.opts[key] = self.opts[key](**self.opts)
        # Check to see if the service is using https so the service_https is
        # set correctly
        if urlparse.urlparse(self.opts["node_endpoint"]).scheme == "https":
            self.opts["service_https"] ="true" 
            
        return pystache.render(self.template, self.opts)
