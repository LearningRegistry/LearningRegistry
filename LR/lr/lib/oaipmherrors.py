'''
Created on Mar 14, 2011

@author: jklo
'''
from datetime import datetime
from pylons import request

class Error(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        self.datetime_now = datetime.utcnow().isoformat()
        self.path_url = request.path_url

class ErrorWithVerb(Error):
    def __init__(self, code, msg, verb):
        Error.__init__(self, code, msg)
        self.verb = verb

class BadVerbError(Error):
    def __init__(self):
        Error.__init__(self, "badVerb", "Illegal OAI Verb")

class BadResumptionTokenError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "badResumptionToken", "Resumption tokens not supported.", verb)

class BadArgumentError(ErrorWithVerb):
    def __init__(self, msg, verb):
        ErrorWithVerb.__init__(self, "badArgument", msg, verb)

class CannotDisseminateFormatError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "cannotDisseminateFormat", "The metadata format identified by the value given for the metadataPrefix argument is not supported by the item or by the repository.", verb)

class IdDoesNotExistError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "idDoesNotExist", "The value of the identifier argument is unknown or illegal in this repository.", verb)

class NoMetadataFormats(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "noMetadataFormats", "No metadata formats exist.", verb)

class NoRecordsMatchError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "noRecordsMatch", "The combination of the values of the from, until, and metadataPrefix arguments results in an empty list.", verb)

class NoSetHierarchyError(ErrorWithVerb):
    def __init__(self, verb):
        ErrorWithVerb.__init__(self, "noSetHierarchy", "The repository does not support sets.", verb)
        
