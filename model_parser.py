#!/usr/bin/python
from pyparsing import *
import re
import codecs


def getFileString(filename):

    #Use codecs to open the files as unicode encoding to deals with googledocs
    #file that using unicode for open and close string.
    file = codecs.open(filename, encoding='utf-8')
    fileString = file.read()
    file.close()

    #Remove the optional X_xxx enxtesion variable from the file string.Formatter    
    fileString = re.sub(r'\s+"X_xxx.*', '', fileString)
    
    #replace the unicode quotation marks with plain one.
    fileString = re.sub(u"\u201c|\u201d", '"', fileString)
    return fileString

def getString(originalText, location, tokens):
    return "".join(tokens)

class ModelParser(object):
    
    
    #Define some string constants
    _KEY_COMMENT = 'keyCcomment'
    _VALUE_COMMENT = 'valueComment'
    _PROPERTY = '_Me_property'
    _KEY = 'key'
    _VALUE = 'value'
    _VALUE_DEFAULT = 'valueDefault'
    _VALUE_TYPE = 'valueType'
    _VALUE_RANGE = 'valueRange'
    _VALUE_TYPE_ARRAY = 'valueTypeArray'
    _VALUE_TYPE_INLINE = 'valueTypeInline'
    _IS_REQUIRED = 'isRequired'
    _IS_IMMUTABLE = 'isImmutable'
    _OBJECT = '_Me_object'
    
    JSON_TYPES =  ['string', 'boolean', 'number', 'array', 'object']
    
    #Define pyparsing variables.
    VAR = Regex('[A-Za-z0-9_.]+')
    INGORE_SPACE = Suppress(ZeroOrMore(White()))
    
    # The quote has to be a regular expression to deal unicode 
    # open and close quotations marks from the googledoc of the spec that uses
    # unicode open and close quotation marks.
    QUOTE = Regex('["'+unichr(0x201c)+unichr(0x201d)+']')
    
    NAME = INGORE_SPACE+Suppress(QUOTE)+VAR+Suppress(QUOTE)+INGORE_SPACE
    NAME.setParseAction(getString)
    
    TYPES =  oneOf(JSON_TYPES)
    TYPES.setParseAction(getString)
        
    JSON_TYPES = (Suppress(QUOTE)+TYPES+Suppress(QUOTE))|TYPES
    JSON_TYPES.setParseAction(getString)
    
    ARRAY = '['+Suppress(QUOTE)+TYPES+Suppress(QUOTE)+']'
    ARRAY.setParseAction(getString)
    
    OBJECT_START = Suppress('{')
    OBJECT_END = Suppress('}')
    COMMENT_START= '//'
    
    KEY = NAME+Suppress(':')
    KEY.setParseAction(getString)
    
    #Forward define of object since a value can be an object.
    OBJECT = Forward()
    
    #inline value are just string inside of a backet.
    INLINE_VALUE = OBJECT_START + \
                originalTextFor(OneOrMore(Word(alphanums)))+OBJECT_END
    INLINE_VALUE.setParseAction(getString)
                
    VALUE = (INLINE_VALUE.setResultsName(_VALUE_TYPE_INLINE)
             |OBJECT.setResultsName(_OBJECT)
             |ARRAY.setResultsName(_VALUE_TYPE_ARRAY)
             |JSON_TYPES.setResultsName(_VALUE_TYPE)
             |NAME.setResultsName(_VALUE_DEFAULT)
            )+ \
             Suppress(','|FollowedBy(OBJECT_END))
    
     # This parser will look string fixed vocabulary which signal the
    # property has defined range of values that are in value_range
    VALUE_RANGE = Combine(Suppress(Regex(u'fixed\s+vocabulary\s+'))+\
              Regex(r'\[[^]]+\]')).setResultsName(_VALUE_RANGE)

    
    IS_REQUIRED = Keyword('required')
    IS_REQUIRED.setParseAction(lambda s, p, t: True)
    
    IS_IMMUTABLE = Keyword('immutable')
    IS_IMMUTABLE.setParseAction(lambda s, p, t: True)
    
    #Parser to extract any useful information from the comments.
    COMMENT_INFO = (Optional(SkipTo(VALUE_RANGE)+
                            VALUE_RANGE.setResultsName(_VALUE_RANGE))+\
                   Optional(SkipTo(IS_REQUIRED)+
                            IS_REQUIRED.setResultsName(_IS_REQUIRED))+\
                   Optional(SkipTo(IS_IMMUTABLE)+
                           IS_IMMUTABLE.setResultsName(_IS_IMMUTABLE))
                    ).setResultsName(_VALUE)
                    
    
    COMMENT_KEY = originalTextFor(COMMENT_START+SkipTo(VALUE))
    COMMENT_VALUE = originalTextFor(COMMENT_START+SkipTo(KEY|OBJECT_END))
    
##    def parseComments(string, position, tokens):
##        comments = re.search(r"[^:}]+", string[position:-1], re.DOTALL).group()
##                            
##        print("-----------------------\n\n"+comments)
##        print("-----------------------\n\n")
##        result = ModelParser.COMMENT_INFO.parseString(comments)
##        return result
##        
##        
##    COMMENT_VALUE.setParseAction(parseComments)
    
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
                ZeroOrMore(Dict(PROPERTY.setResultsName(_PROPERTY)))+
                OBJECT_END
               ).setResultsName(_OBJECT)
    
   
            
    
    def __init__(self, string=None, filePath=None):
        """Class that parse data models from the spec for object validation.
          string: String represention of model based on Dan Rehak JSON like
                  format.
                
          filePath: Full path of a file that contains Dan Rehak JSON like
                   data model"""
                
        self._fileString = None
        self._modelName = None
        self._parseResult = None
        self._propertyDict = {}
        
        if string is not None:
            self._fileString = string
            
        if filePath is not None:
            self._fileString = getFileString(filePath)
      
        #parse the models
        if self._fileString is not None:
            self._extractData()
        
        
    def _extractData(self):
        if self._parseResult is not None:
            return
        self._parseResult =  ModelParser.OBJECT.parseString(self._fileString)
        self._modelName = self._parseResult.doc_type.value.valueDefault
        #For some reason pyparsing parseAction does no like to return
        #a list. So look for all valueRange string and eval to a list.
        for property in self._parseResult:
            commentInfo = ModelParser.COMMENT_INFO.parseString(
                    property[ModelParser._VALUE_COMMENT])
            print("---------------\n")
            print property.asDict()
            print("+++++++++++++++++++++\n") 
            print commentInfo.asDict()
          
            #replace any value range string with a tubple
            if self._VALUE_RANGE in commentInfo.asDict().keys():
                rangeString = commentInfo[self._VALUE_RANGE]
                print (":::::::::::\n"+rangeString)
                rangeString = re.sub(r"\s+|/", '', rangeString)                     
                commentInfo[self._VALUE_RANGE] = tuple(eval(rangeString))

            self._parseResult[property[self._KEY]] = property+commentInfo
               
            print("******\n\n") 
            print property.asDict()
    
    model = property(lambda self:self._parseResult, None, None, None)
  
    