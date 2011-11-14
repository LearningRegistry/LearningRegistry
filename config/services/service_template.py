
import abc
import pystache
import types
import urlparse
import pprint

class ServiceTemplate():
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        self.template = '''
{
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
