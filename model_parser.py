#!/usr/bin/python
from pyparsing import *
import re
import codecs
import json

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
    _KEY = '_Me_key'
    _VALUE = '_Me_value'
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
    QUOTED_TYPES = (Suppress(QUOTE)+TYPES+Suppress(QUOTE)) 
       
    JSON_TYPES = QUOTED_TYPES|TYPES
    JSON_TYPES.setParseAction(getString)
    
    
    OBJECT_START = Suppress('{')
    OBJECT_END = Suppress('}')
    COMMENT_START= '//'
    
    KEY = NAME+Suppress(':')
    KEY.setParseAction(getString)
    
    #Forward define of object since a value can be an object.
    OBJECT = Forward()
    
    ARRAY = '['+(QUOTED_TYPES.setParseAction(getString)|\
                (Optional(COMMENT_START+FollowedBy(OBJECT)).setResultsName(_VALUE_COMMENT)
                +OBJECT))+']'
    
    
    #inline value are just string inside of a backet.
    INLINE_VALUE = OBJECT_START + \
                originalTextFor(OneOrMore(Word(alphanums)))+OBJECT_END
    INLINE_VALUE.setParseAction(getString)
                
    VALUE = (JSON_TYPES.setResultsName(_VALUE_TYPE)
             |NAME.setResultsName(_VALUE_DEFAULT)
             |ARRAY.setResultsName(_VALUE_TYPE_ARRAY)
             |INLINE_VALUE.setResultsName(_VALUE_TYPE_INLINE)
             |OBJECT.setResultsName(_OBJECT)
            )+ \
             Suppress(','|FollowedBy(COMMENT_START|OBJECT_END))
    
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
                    
    COMMENT = Combine(OneOrMore(White()+COMMENT_START+SkipTo(LineEnd())))
    #COMMENT_KEY = originalTextFor(COMMENT_START+SkipTo(LineEnd()))
    #COMMENT_VALUE = originalTextFor(COMMENT_START+SkipTo(KEY|ARRAY|OBJECT_END))

    
    PROPERTY =Group((KEY.setResultsName(_KEY)+
                     COMMENT.setResultsName(_KEY_COMMENT)+
                     VALUE.setResultsName(_VALUE)+
                     COMMENT.setResultsName(_VALUE_COMMENT)
                     )|
                    (KEY.setResultsName(_KEY)+
                     VALUE.setResultsName(_VALUE)+
                     COMMENT.setResultsName(_VALUE_COMMENT)
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
        self._parseResults = None
        # The model info is a copy of the parseResults where some duplicate
        # information has been remove. And some other cleaned up, like the
        # range of valid values.
        self._modelInfo = None
        
        if string is not None:
            self._fileString = string
            
        if filePath is not None:
            self._fileString = getFileString(filePath)
      
        #parse the models
        if self._fileString is not None:
            self._extractData()
        
    def _cleanup(self, results):
        """ Go through all the keys and remove some duplicate infomation
            in key, value, and added parsing generated keys like _Me_object, 
            and _Me_property.
        """
        for key in results.asDict().keys():
            if key in [self._KEY, self._VALUE, self._OBJECT, self._PROPERTY]:
                results.pop(key)
                continue
            if isinstance(results[key], ParseResults):
                self._cleanup(results[key])
            
    def _extractCommentInfo(self, results):
        """Extracts any additional info from the comments"""
        
        for key in results.keys():
            #See if there is any comment to extract info from.
            if self._VALUE_COMMENT in results[key].keys():
                commentString = results[key][self._VALUE_COMMENT]
                commentInfo = self.COMMENT_INFO.parseString(commentString)
                
                # For some reason pyparsing parseAction does no like to return
                # a list. So look for any valueRange string and eval to a list,
                # and save the list as a tuple
                if self._VALUE_RANGE in commentInfo.keys():
                    rangeString = commentInfo[self._VALUE_RANGE]
                    #Clean the range string, remove extra space and errand char.
                    rangeString = re.sub(r"\s+|/", '', rangeString)                     
                    commentInfo[self._VALUE_RANGE] = tuple(eval(rangeString))
                
                #Cleanup comment before merging
                self._cleanup(commentInfo)
                    
                #Merge any info extracted from the comment.
                results[key] = results[key] + commentInfo
        return results
        
    def _extractData(self):
        """Parses the spec data model"""
        
        #Don't do anything if the data is already parsed.
        if self._parseResults is not None and self._modelInfo is not None:
            return
        
        self._parseResults =  ModelParser.OBJECT.parseString(self._fileString)
        #Get the name of the model.    
        if 'doc_type' in self._parseResults.keys():
            self._modelName = self._parseResults.doc_type.valueDefault
        
        self._modelInfo = self._parseResults.copy()
        
        
        self._cleanup(self._modelInfo)
        self._extractCommentInfo(self._modelInfo)
       

    def _getModelInfo(self):
        self._extractData()
        return self._modelInfo
    
    modelInfo = property(_getModelInfo, None, None, None)
    
    def asJSON(self):
        """Transforms the parsed model to a valid JSON representation."""
        
        def parseResultsToDict(results):
            if(results is None or (isinstance(results, ParseResults)== False)):
                return results
            
            dictionary = results.asDict()
            #Go down to each value and convert them to dictionary.
            for key in dictionary.keys():
                dictionary[key] = parseResultsToDict(dictionary[key]) 
            
            return dictionary
        
        return json.dumps(parseResultsToDict(self._modelInfo), indent=4)
    
    def asXML(self):
        return self._modelInfo.asXML(doctag=self._modelName,namedItemsOnly=True)
    
  
def extractModels():
    for s in models:
        rese= re.search('"doc_type"\s*:\s*"(?P<name>[^"]+)', s)
        if rese == None:
            continue
        file = codecs.open('./models/'+rese.group('name'), encoding='utf-8', mode='w')               
        file.write(s)
        file.close()

if __name__== "__main__":
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filepath", 
                      help="The full path of the data model spec definition.",
                      metavar="FILE")
                    
    parser.add_option("-s", "--string", dest="string",
                      help="String representation of the data model spec definition")
                
    parser.add_option("-j", "--json", dest="json", action = "store_true", 
                      default=False,
                      help="Show a json representation of data model spec.")
                    
    parser.add_option("-v", "--validate", dest="source",
                      help="""Validates a JSON object against the spec data model
                            The source JSON object can be a file or a string 
                            representation of the JSON object.
                            """
                        )
    
    (options, args) = parser.parse_args()
    
    model = None
    
    if options.filepath is not None:
        model = ModelParser(filePath=options.filepath)
        
    elif options.string is not None:
        model = ModelParser(string = options.string)
        
    if model == None:
        print("Failed to parse data model spec.")
        exit()
    
    if options.json == True:
        print model.asJSON()
    
    