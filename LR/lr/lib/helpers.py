"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

def convertToISO8601UTC(datetime=None):
    if datetime != None:
        return (datetime - datetime.utcoffset()).replace(tzinfo=None)
    return datetime
        
def convertToISO8601Zformat(datetime=None):
    if datetime != None:
        return ((datetime - datetime.utcoffset()).replace(tzinfo=None)).isoformat() + "Z" 
    return datetime
