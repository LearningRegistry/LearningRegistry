
from datetime import datetime, timedelta
import time
import urllib2
import urllib
import urlparse
import json
import logging
import types
from iso8601 import iso8601

log = logging.getLogger(__name__)
"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password
from iso8601.iso8601 import ISO8601_REGEX
import re
from stream import StreamingCouchDBDocHandler


class document:
    def __init__(self,data):
        if data.has_key('id'):
            self.id = data['id']
        if data.has_key('key'):
            self.key=data['key']
        if data.has_key('doc'):
            self.doc=data['doc']        

def fixUtf8(input):
    if isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def getServiceDocument(serviceName):
    from lr.model.base_model import appConfig
    json_headers = { "Content-Type": "application/json; charset=\"utf-8\"" }
    url = "{0}/{1}/{2}".format(appConfig['couchdb.url'],appConfig['couchdb.db.node'],urllib.quote(serviceName))
    req = urllib2.Request(url=url, headers=json_headers)
    res = urllib2.urlopen(req)
    return json.load(res)


def getView(database_url, view_name, method="GET", documentHandler=None, **kwargs):    
    json_headers = { "Content-Type": "application/json; charset=\"utf-8\"" }
    get_head_args = ["key", "startkey", "startkey_docid", "endkey", 
                     "endkey_docid", "limit", "stale", "descending", "skip", 
                     "group", "group_level", "reduce", "include_docs", 
                     "inclusive_end", "update_seq"]
    post_args = ["keys"]
    # Certain keys must be proper JSON values
    for foo in kwargs:
        if foo in ['startkey','endkey','key']:
            kwargs[foo] = json.dumps(kwargs[foo])
    
    query_args = {}
    post_data = {}
    for key in kwargs:
        val = kwargs[key]
        if key in get_head_args:
            if isinstance(val, types.BooleanType):
                query_args[key] = repr(val).lower()
            else:
                query_args[key] = val
        if key in post_args:
            post_data[key] = val
            
    if method is "POST" or post_data != {}:
        view_url = '?'.join(['/'.join([database_url,view_name]),urllib.urlencode(query_args)]) 
        post_data = json.dumps(post_data)
        log.debug("POST "+view_url)
        log.debug("DATA " + post_data)
        view_req = urllib2.Request(view_url, data=post_data, headers=json_headers)
    else:
        view_url = '?'.join(['/'.join([database_url,view_name]),urllib.urlencode(query_args)]) 
        view_req = urllib2.Request(view_url, headers=json_headers)
        log.debug("GET "+view_url)   
    resp = urllib2.urlopen(view_req)
    
    dh = StreamingCouchDBDocHandler(documentHandler)
    return dh.generator(resp)
    
#    for data in resp:
#        length = data.rfind(',')
#        if length > 0:
#            data = data[:length]        
#        try:
#            data = json.loads(data)
#            doc = document(data)
#            yield doc
#        except ValueError as e:
#            log.debug(repr(e))

            #pass#skip first and final chunks
class ParseError(Exception):
    """Raised when there is a problem parsing a date string"""

def importModuleFromFile(fullpath):
    """Loads  and returns module defined by the file path. Returns None if file could 
    not be loaded"""
    import os
    import sys
    
    
    
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
    arg = dateTimeArg
    if isinstance(arg, (types.StringTypes, unicode)) == True:
        try:
            arg = iso8601.parse_date(arg)
        except:
            pass
    
    if isinstance(arg, datetime) == True and arg.tzinfo is not None:
        dateUTC = arg - arg.utcoffset()
        dateUTC_noTZ = datetime(dateUTC.year, dateUTC.month, dateUTC.day, dateUTC.hour, dateUTC.minute, dateUTC.second, dateUTC.microsecond)
        return dateUTC_noTZ

    return dateTimeArg
        
def convertToISO8601Zformat(dateTimeArg):
    if isinstance(dateTimeArg, datetime) ==True:
        return convertToISO8601UTC (dateTimeArg).isoformat()+ "Z" 
    return dateTimeArg

def harvestTimeFormat(dateTimeArg):
    if isinstance(dateTimeArg, datetime) ==True:
        fmtStr = getHarvestDatetimeFormatString()
        utcdate = convertToISO8601UTC (dateTimeArg)
#        import logging
#        log = logging.getLogger(__name__)
#        log.exception(utcdate.utctimetuple())
        return time.strftime(fmtStr,utcdate.utctimetuple())
    return dateTimeArg
    
def nowToISO8601Zformat():
    return datetime.utcnow().isoformat()+"Z"

def getISO8601Granularity(iso8601string):
    '''Determine the precision of an ISO8601 datetime string'''
    
    def _getPrecision(gran, granule):
        if gran.precision == None:
            return len(granule)
        else:
            return gran.precision

    if not isinstance(iso8601string, basestring):
        raise ParseError("Expecting a string %r" % iso8601string)
    m = ISO8601_REGEX.match(iso8601string)
    if not m:
        raise ParseError("Unable to parse date string %r" % iso8601string)
    groups = m.groupdict()
    sandsOfTime = [
                   Granularity("year",  4, 1), 
                   Granularity("month", 2, 2), 
                   Granularity("day",   2, 3), 
                   Granularity("hour",  2, 4),
                   Granularity("minute",2, 5),
                   Granularity("second",2, 6),
                   Granularity("fraction", None, 7) ]
    curGrain = Granularity()
    for s in sandsOfTime:
        if groups[s.granule] != None:
            curGrain.granule = s.granule
            curGrain.precision = _getPrecision(s, groups[s.granule])
            curGrain.order = s.order
        else:
            break
    return curGrain

_DATETIME_REPLACEMENT_REGEX = re.compile(r"[YMDhms]")

def getHarvestServiceGranularity():
    '''Determines the Granularity object of 8601 time format specified by Basic Harvest'''
    format = getDatetimePrecision()
    return getISO8601Granularity(re.sub(_DATETIME_REPLACEMENT_REGEX, "1", format))
    
    
def getDatetimePrecision():
    '''Get's the ISO8601 Time format string as stored in the Basic Harvest service descriptor.
    
        FIXME: Basic Harvest is currently missing it's service description document, so this method currently
        always returns YYYY-MM-DDThh:mm:ssZ'''
    granularity = "YYYY-MM-DDThh:mm:ssZ"
#    from lr.model import LRNode
#    for s in LRNode.nodeServices:
#        if (s.has_key("service_name") and s["service_name"] == "Basic Harvest" and 
#            s.has_key("service_data") and s["service_data"].has_key("granularity") and 
#            s["service_data"]["granularity"] != None):
#                granularity = s["service_data"]["granularity"]
#                break
    return granularity
    
    
def getHarvestDatetimeFormatString():
    precision = getDatetimePrecision()
    precision = re.sub("[Y]{4}", "%Y", precision)
    precision = re.sub("[M]{2}", "%m", precision)
    precision = re.sub("[D]{2}", "%d", precision)
    precision = re.sub("[h]{2}", "%H", precision)
    precision = re.sub("[m]{2}", "%M", precision)
    precision = re.sub("(?:)[s]{2}", "%S", precision)
    return precision

class Granularity(object):
    def __init__(self, granule=None, precision=None, order=0):
        self.granule = granule
        self.precision = precision
        self.order = order
    
    def __cmp__(self, other):
        if isinstance(other, Granularity):
            if self.order == other.order:
                return cmp(self.precision, other.precision)
            else:
                return cmp(self.order, other.order)
        else:
            return cmp(str(self), str(other))
        
