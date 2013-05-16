"""Setup the LR application"""
import logging

import pylons.test

from lr.config.environment import load_environment
from lr.plugins import init_plugins
from lr.model.resource_data_monitor import monitorResourceDataChanges
log = logging.getLogger(__name__)


def setup_app(command, conf, vars):
    """Place any commands to setup lr here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    monitorResourceDataChanges()
    print("got here")
    assert init_plugins() is not None, "Plugins not Loading!!!!"
