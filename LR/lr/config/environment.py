"""Pylons environment configuration"""
import os

from mako.lookup import TemplateLookup
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error

import lr.lib.app_globals as app_globals
import lr.lib.helpers
from lr.config.routing import make_map
import logging
import logging.config

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()
    
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])
    try:    
        logging.config.fileConfig(global_conf['__file__'])
    except:
        pass#to make unit tests run
    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='lr', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = lr.lib.helpers
    config['pylons.response_options']['content-type'] = 'application/json'
    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)
    

    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])
    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    import couchdb
    import lr.lib.helpers as helpers
    server = couchdb.Server(config['couchdb.url.dbadmin'])
    db = server[config['couchdb.db.node']]
    doc = db[config['lr.nodestatus.docid']]
    doc['start_time'] = helpers.nowToISO8601Zformat()
    db.save(doc)  

    return config
