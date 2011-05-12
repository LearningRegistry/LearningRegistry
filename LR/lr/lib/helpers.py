
from datetime import datetime, timedelta
import time
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

def convertToISO8601UTC (dateTimeArg):
    """This method assumes that the datetime is local naive time."""
    if isinstance(dateTimeArg, datetime) == True:
        dateUTC = datetime.utcfromtimestamp(time.mktime(dateTimeArg.timetuple()))
        #Add the macroseconds back since hte mktime conversion loses it
        return (dataUTC + timedelta(0, 0, datetimeArg.microsecond))
    return dateTimeArg
        
def convertToISO8601Zformat(dateTimeArg):
    if isinstance(dateTimeArg, datetime) ==True:
        return convertToISO8601UTC (dateTimeArg).isoformat()+ "Z" 
    return dateTimeArg
    
def nowToISO8601Zformat():
    return datetime.utcnow().isoformat+"Z"
