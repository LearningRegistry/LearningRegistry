"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper
import logging
from lr.lib import helpers as h
log = logging.getLogger(__name__)
def make_map(config):
    """Create, configure and return the routes Mapper"""
    from pylons import config as c    
    c.update(config)
    from lr.model import LRNode

    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.append_slash = True
    map.resource('filter', 'filters', controller='contrib/filters', 
        path_prefix='/contrib', name_prefix='contrib_')
    map.resource('status','status')
    map.resource('distribute','distribute')
    if not LRNode.nodeDescription.gateway_node:
        map.resource('publish','publish')
        map.resource('obtain','obtain')        
        map.resource('description','description')
        map.resource('services','services')
        map.resource('policy','policy')
        map.resource('harvest','harvest')
        # Value added services
        map.resource('OAI-PMH', 'OAI-PMH')
        map.resource('swordservice','swordservice')
        map.resource('slice', 'slice')
    
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')
    
    # CUSTOM ROUTES HERE
    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')
    return map
