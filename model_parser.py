#!/usr/bin/python
from pyparsing import *
import re
import codecs


def GeFileString(filename):
    
    #Use codecs to open the files as unicode encoding to deals with googledocs
    #file that using unicode for open and close string.
    file = codecs.open(filename, encoding='utf-8')
    fileString = file.read()
    file.close()

    #Remove the optional X_xxx enxtesion variable from the file string.Formatter    
    fileString = re.sub(r'\s+"X_xxx.*', '', fileString)
    return fileString

def getString(originalText, location, tokens):
    return "".join(tokens)

class ModelParser(object):
    
    #Define some string constants
    _KEY_COMMENT = 'key_comment'
    _VALUE_COMMENT = 'value_comment'
    _PROPERTY = 'property'
    _KEY = 'key'
    _VALUE = 'value'
    _VALUE_DEFAULT = 'value_default'
    _VALUE_TYPE = 'value_type'
    _VALUE_TYPE_ARRAY = 'value_type_array'
    _VALUE_TYPE_INLINE = 'value_type_inline'
    _OBJECT = 'object'
    
    #Define pyparsing variables.
                
    VAR = Regex('[A-Za-z0-9_.]+')
    INGORE_SPACE = Suppress(ZeroOrMore(White()))
    
    # The quote has to be a regular expression to deal unicode 
    # open and close quotations marks from the googledoc of the spec that uses
    # unicode open and close quotation marks.
    QUOTE = Regex('["'+unichr(0x201c)+unichr(0x201d)+']')
    
    NAME = INGORE_SPACE+Suppress(QUOTE)+VAR+Suppress(QUOTE)+INGORE_SPACE
    NAME.setParseAction(getString)
    
    TYPES =  oneOf(['string', 'boolean', 'number', 'array', 'object'])
    TYPES.setParseAction(getString)
        
    JSON_TYPES = (Suppress(QUOTE)+TYPES+Suppress(QUOTE))|TYPES
    JSON_TYPES.setParseAction(getString)
    
    ARRAY = '['+Suppress(QUOTE)+TYPES+Suppress(QUOTE)+']'
    ARRAY.setParseAction(getString)
    
    OBJECT_START = Suppress('{')
    OBJECT_END = Suppress('}')
    COMMENT_START= '//'
    
    KEY = NAME+Suppress(':')
   
    
    #Forward define of object since a value can be an object.
    OBJECT = Forward()
    
    #inline value are just string inside of a backet.
    INLINE_VALUE = OBJECT_START + \
                originalTextFor(OneOrMore(Word(alphanums)))+OBJECT_END
                
    VALUE = (JSON_TYPES.setResultsName(_VALUE_TYPE)
             |NAME.setResultsName(_VALUE_DEFAULT) \
             |ARRAY.setResultsName(_VALUE_TYPE_ARRAY)
             |INLINE_VALUE.setResultsName(_VALUE_TYPE_INLINE)
             |OBJECT.setResultsName(_OBJECT)) + \
             Suppress(','|FollowedBy(OBJECT_END))
    
    COMMENT_KEY = originalTextFor(COMMENT_START+SkipTo(VALUE))
    COMMENT_VALUE = originalTextFor(COMMENT_START+SkipTo(KEY|OBJECT_END))
    
    
    PROPERTY =Group((KEY.setResultsName(_KEY)+
                     COMMENT_KEY.setResultsName(_KEY_COMMENT)+
                     VALUE.setResultsName(_VALUE)+
                     COMMENT_VALUE.setResultsName(_VALUE_COMMENT)
                     )|
                    (KEY.setResultsName(_KEY)+
                     VALUE.setResultsName(_VALUE)+
                     COMMENT_VALUE.setResultsName(_VALUE_COMMENT)
                     )|
                     (KEY.setResultsName(_KEY)+
                      VALUE.setResultsName(_VALUE)
                     )
                    )    
    PROPERTY.setResultsName(_PROPERTY)
    
    OBJECT << (OBJECT_START+
                ZeroOrMore(PROPERTY.setResultsName(_PROPERTY))+
                OBJECT_END
               ).setResultsName(_OBJECT)
    
    def __init__(self, string, filePath=None):
        """Class that parse data models from the spec for object validation.
          string: String represention of model based on Dan Rehak JSON like
                  format.
                
          filePath: Full path of a file that contains Dan Rehak JSON like
                   data model"""
                
        self._fileString = ''
        self._parseResult = None
        #List spec the keys in the objects
        self._keys = []
        
        #List of keys that are required for a valid object.
        self._requiredKeys = []
        
        #List of keys are immutable.
        self._immutableKeys = []
        
        # Dictionary of keys that have defualt values and their 
        # defaults values
        self._keyDefaultValues = {}
        
        # Dictionary of keys that has range of values and their list of
        # values
        self._keyValueRange = {}
        
        #Self key comments
        self._keyComment = {}
        
        #comments on the value
        self._valueComment = {}
        
        if filename is not None:
            self._fileString = GetFileString(filename)
        if string is not None:
            self._fileString = string
            
        #parse the models
        _extractData()
        
    
    def _extractCommentInfo(key, comment):
            
        if re.search('required', comment) is not None :
            self._requiredKeys.append(key)
        
        if re.search('immutable', comment) is not None:
            self._immutableKeys.append(key)
        
        if re.search(r'fixed\s+vocabulary', comment) is not None:
            self._keyDefaultValues[key] = commentInfo.defaultValue
            
        
    def _extractData(self):
        if self._parseResult is not None:
            return
        
        for p in parseResult:
            property = p.asDict()
            key = property[_KEY]
            self._keys.append(key)
            
            if _VALUE_COMMENT in poperty.keys():
                value_comment = property[_VALUE_COMMENT]
                self._valueComment[key] = value_comment
                _extractCommentInfo(key, value_comment)
                
            if _KEY_COMMENT in property.keys():
                self._keyComment[key] = poperty[_KEY_COMMENT]

            
            
    def _getParseResult(self):
        if self._parseResult is None:
            self._parseResult = OBJECT.parseString(self._fileString)
        return _parseResult
    
    def _getKeys(self):
        if self._keys is None:
            self._keys =[]
            self._extract_data()
    
    parseResult = property(_getParseResult, None, None, None)
    keys = property(_getKeys, None, None, 
                    "List the object keys specified in the spec")
    