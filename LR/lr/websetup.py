"""Setup the LR application"""
import logging

import pylons.test

from lr.config.environment import load_environment
from lr.plugins import init_plugins

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup lr here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)

    assert init_plugins() is not None, "Plugins not Loading!!!!"

    # Start process that listens the resource_data  databasechange feed in order 
    # to mirror distributable/resource_data type documents, udpate views and fire
    # periodic distribution.
    