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
    
    
    def mapResource(config_key, member_name, collection_name):
        try:
            service_doc_id = config[config_key]
            service_doc = h.getServiceDocument(service_doc_id)
            if service_doc is not None and service_doc["active"]:
                map.resource(member_name, collection_name)
                if member_name == 'swordservice':
                    map.connect("/swordpub",controller='swordservice',action='create')
                
                if member_name == 'distribute':
                    map.connect("/destination", controller='distribute', action='destination',
                                          conditions=dict(method='GET'))
                log.info("Enabling service route for: {0} member: {1} collection: {2}".format(service_doc_id, member_name, collection_name))
            else:
                log.info("Service route for {0} is disabled".format(service_doc_id))
        except:
                log.exception("Exception caught: Not enabling service route for config: {0} member: {1} collection: {2}".format(config_key, member_name, collection_name))
            
    
    map.resource('filter', 'filters', controller='contrib/filters', 
        path_prefix='/contrib', name_prefix='contrib_')
    mapResource('lr.status.docid', 'status','status')
    mapResource('lr.distribute.docid','distribute','distribute')
    if not LRNode.nodeDescription.gateway_node:
        mapResource('lr.publish.docid', 'publish','publish')
        mapResource('lr.obtain.docid', 'obtain','obtain')        
        mapResource('lr.description.docid', 'description','description')
        mapResource('lr.services.docid', 'services','services')
        mapResource('lr.policy.docid', 'policy','policy')
        mapResource('lr.harvest.docid','harvest','harvest')
        # Value added services
        mapResource('lr.oaipmh.docid', 'OAI-PMH', 'OAI-PMH')
        mapResource('lr.slice.docid', 'slice', 'slice')
        mapResource('lr.sword.docid', 'swordservice','swordservice')    
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
