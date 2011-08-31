'''
Created on Mar 14, 2011

@author: jklo
'''
from datetime import datetime
from pylons import request

class Error(Exception):
    def __init__(self, code, msg, **kwargs):
        Exception.__init__(self)
        self.code = code
        self.msg = msg
        self.message = msg
        self.datetime_now = datetime.utcnow().isoformat()
        self.response_date = self.datetime_now
        
        if "req" in kwargs and kwargs["req"] is not None:
            self.path_url = kwargs["req"].path_url
        else:
            self.path_url = request.path_url

class ErrorWithVerb(Error):
    def __init__(self, code, msg="", verb="unknown", **kwargs):
        Error.__init__(self, code, msg, **kwargs)
        self.verb = verb

class BadVerbError(Error):
    def __init__(self, **kwargs):
        Error.__init__(self, "badVerb", "Illegal OAI Verb", **kwargs)

class BadResumptionTokenError(ErrorWithVerb):
    def __init__(self, verb, **kwargs):
        if 'msg' not in kwargs:
            kwargs['msg'] = "Resumption tokens not supported."

        ErrorWithVerb.__init__(self, "badResumptionToken", verb=verb, **kwargs)

class BadArgumentError(ErrorWithVerb):
    def __init__(self, msg, verb, **kwargs):
        ErrorWithVerb.__init__(self, "badArgument", msg, verb, **kwargs)

class CannotDisseminateFormatError(ErrorWithVerb):
    def __init__(self, verb, **kwargs):
        ErrorWithVerb.__init__(self, "cannotDisseminateFormat", "The metadata format identified by the value given for the metadataPrefix argument is not supported by the item or by the repository.", verb, **kwargs)

class IdDoesNotExistError(ErrorWithVerb):
    def __init__(self, verb, **kwargs):
        ErrorWithVerb.__init__(self, "idDoesNotExist", "The value of the identifier argument is unknown or illegal in this repository.", verb, **kwargs)

class NoMetadataFormats(ErrorWithVerb):
    def __init__(self, verb, **kwargs):
        ErrorWithVerb.__init__(self, "noMetadataFormats", "No metadata formats exist.", verb, **kwargs)

class NoRecordsMatchError(ErrorWithVerb):
    def __init__(self, verb, **kwargs):
        ErrorWithVerb.__init__(self, "noRecordsMatch", "The combination of the values of the from, until, and metadataPrefix arguments results in an empty list.", verb, **kwargs)

class NoSetHierarchyError(ErrorWithVerb):
    def __init__(self, verb, **kwargs):
        ErrorWithVerb.__init__(self, "noSetHierarchy", "The repository does not support sets.", verb, **kwargs)
        
