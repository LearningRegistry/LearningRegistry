
import abc
import pystache
import types

class ServiceTemplate():
    __metaclass__ = abc.ABCMeta
    template = '''
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
    service_data_template = None
    authz_data_template = '''{{authz}}'''

    def _optsoverride(self):
        return {}
    
    def _servicedata(self,**kwargs):
        if self.service_data_template != None:
            return pystache.render(self.service_data_template, kwargs)
        return None
    
    def _authz(self, **kwargs):
        if self.authz_data_template != None:
            if 'authz' in kwargs and isinstance(kwargs['authz'], types.ListType):
                kwargs['authz'] = ','.join(map(lambda x: '"%s"' % x, kwargs['authz']))
            
            return pystache.render(self.authz_data_template, kwargs)
        return None

    opts = {
        "scope": "node",
        "active": "false",
        "service_id": None,
        "service_type": "access",
        "service_name": None,
        "service_version": None,
        "node_endpoint": None,
        "service_endpoint": None,
        "authz": ["none"],
        "service_authz": _authz,
        "service_key": "false", 
        "service_https": "false",
        "service_data": _servicedata
    }
    
 
    
    def render(self, **kwargs):
        self.opts.update(self._optsoverride())
        funcs = []
        for key in self.opts.keys():
            if key in kwargs:
                if isinstance(kwargs[key], types.BooleanType):
                    self.opts[key] = repr(kwargs[key]).lower()
                else:
                    self.opts[key] = kwargs[key]
                
            if isinstance(self.opts[key], types.FunctionType):
                funcs.append(key)
        
        for key in funcs:
            self.opts[key] = self.opts[key](self, **self.opts)
                   
        return pystache.render(self.template, self.opts)
        