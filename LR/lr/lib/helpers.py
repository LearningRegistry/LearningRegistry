"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
def importModuleFromFile(fullpath):
    """Loads  and returns module defined by the file path. Returns None if file could 
    not be loaded"""
    import os
    import sys
    import logging
    log = logging.getLogger(__name__)
    
    sys.path.append(os.path.dirname(fullpath))
    
    module = None
    try:
        module = __import__(os.path.splitext(os.path.basename(fullpath))[0])
 
    except Exception as ex:
        log.exception("Failed to load module:\n"+ex)
    finally:
        del sys.path[-1]
        return module
