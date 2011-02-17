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

class ObjectModelParseException(Exception):
    pass

def isOfJSONType(object, type):
    if type == 'string':
        return (isinstance(object, str) or
                isinstance(object, unicode))
    elif type == 'number':
        return (isinstance(object, float) or
                isinstance(object, int) or
                isinstance(object, long))
    elif type == 'boolean':
        return isinstance(object, bool)
    elif type =='array':
        return (isinstance(object, list) or
                isinstance(object, tuple))
    elif type == 'object':
        return isinstance(object, dict)
    
        
class ModelParser(object):
        
    
    #Define some string constants
    _KEY_COMMENT = 'keyCcomment'
    _VALUE_COMMENT = 'valueComment'
    _PROPERTY = '_Me_property'
    _KEY = '_Me_key'
    _VALUE = '_Me_value'
    _VALUE_DEFINED = 'value'
    _VALUE_TYPE = 'type'
    _VALUE_RANGE = 'valueRange'
    _VALUE_TYPE_ARRAY = 'valueTypeArray'
    _VALUE_TYPE_INLINE = 'valueTypeInline'
    _IS_REQUIRED = 'isRequired'
    _IS_IMMUTABLE = 'isImmutable'
    _OBJECT = '_Me_object'
    _DESCRIPTION = 'description'
    
    JSON_TYPES =  ['string', 'boolean', 'number', 'array', 'object']
    
    #Define pyparsing variables.
    VAR = Regex('[A-Za-z0-9_.]+')
    INGORE_SPACE = Suppress(ZeroOrMore(White()))
    
    #Format of extension keys.
    EXTENSION_VAR = re.compile('^X_')
    
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
    
    ARRAY = '['+(QUOTED_TYPES.setParseAction(getString).setResultsName(_VALUE_TYPE)|\
                (Optional(COMMENT_START+FollowedBy(OBJECT)).setResultsName(_VALUE_COMMENT)
                +OBJECT))+']'
    
    
    #inline value are just string inside of a backet.
    INLINE_VALUE = OBJECT_START + \
                originalTextFor(OneOrMore(Word(alphanums)))+OBJECT_END
    INLINE_VALUE.setParseAction(getString)
                
    VALUE = (JSON_TYPES.setResultsName(_VALUE_TYPE)
             |NAME.setResultsName(_VALUE_DEFINED)
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
        
    def _cleanup(self, parseResults):
        """ Go through all the keys and remove some duplicate infomation
            in key, value, and added parsing generated keys like _Me_object, 
            and _Me_property.
        """
        for key in parseResults.asDict().keys():
            if key in [self._KEY, self._VALUE, self._OBJECT, self._PROPERTY]:
                parseResults.pop(key)
                continue
            if isinstance(parseResults[key], ParseResults):
                self._cleanup(parseResults[key])

    
    def _commentsToDescription(self, parseResults):
        """Collapases key and value comments into one description string"""
        
        commentString = ''
        if self._KEY_COMMENT in parseResults.keys():
            commentString = parseResults[self._KEY_COMMENT]+".  "
            #remove the _KEY_COMMENTS from list of keys.
            parseResults.pop(self._KEY_COMMENT)
            
        if self._VALUE_COMMENT in parseResults.keys():
            commentString = commentString + parseResults[self._VALUE_COMMENT]
            parseResults.pop(self._VALUE_COMMENT)

        if len(commentString) == 0:
            return 
        
        #Clean up the comment string, remove the // and extra spaces.
        commentString = re.sub(r'//', '', commentString)
        commentString = re.sub('\s+', ' ',commentString)
        parseResults[self._DESCRIPTION] = commentString
            
    
    
    def _extractCommentInfo(self, parseResults):
    
        """Extracts any additional info from the comments"""
        
        for key in parseResults.keys():
            if isinstance(parseResults[key], ParseResults) == True:
                self._extractCommentInfo(parseResults[key])
            else:
                continue
            
            #See if there is any comment to extract info from.
            if self._VALUE_COMMENT in parseResults[key].keys():
                commentString = parseResults[key][self._VALUE_COMMENT]
                #Parse the comments for any additional info
                commentInfo = self.COMMENT_INFO.parseString(commentString)
                
                # For some reason pyparsing parseAction does no like to return
                # a list. So look for any valueRange string and eval to a list,
                # and save the list as a tuple
                if self._VALUE_RANGE in commentInfo.keys():
                    rangeString = commentInfo[self._VALUE_RANGE]
                    #Clean the range string, remove extra space and errand char.
                    rangeString = re.sub(r"\s+|/", ' ', rangeString)                     
                    commentInfo[self._VALUE_RANGE] = tuple(eval(rangeString))

                #Cleanup comment info before merging
                self._cleanup(commentInfo)

                #Merge any info extracted from the comment.
                parseResults[key] = parseResults[key] + commentInfo
                #put the comments to a desciption key.
                self._commentsToDescription(parseResults[key])
                
        return parseResults
        
    
    def _extractObjectType(self, parseResults):
        """Futher parse and clean values of type object"""
        object = None
        for key in parseResults.keys():
            if self._VALUE_TYPE_INLINE in parseResults[key].keys():
                object = parseResults[key][self._VALUE_TYPE_INLINE]
                parseResults[key][self._VALUE_TYPE] = 'object'
                #remove the old inline key.
                parseResults[key].pop(self._VALUE_TYPE_INLINE)
                
            # If the object is parse result process it futher to 
            # extract comments or array info
            if isinstance(object, ParseResults) == True:
                self._extractObjectType(object)
                self._extractArrayType(object)
                #parseResults[key][self._VALUE_DEFINED] = object
    
    def _extractArrayType(self, parseResults):
        """Futher parse and clean values of type array"""
        array = None
        for key in parseResults.keys():
            if isinstance(parseResults[key], ParseResults) == False:
                continue
            
            if self._VALUE_TYPE_ARRAY in parseResults[key].keys():
                array = parseResults[key][self._VALUE_TYPE_ARRAY]
                parseResults[key][self._VALUE_TYPE] = 'array'
                #remove the old inline key.
                parseResults[key].pop(self._VALUE_TYPE_ARRAY)
                
            # If the object is parse result process it futher to 
            # extract comments or array info
            if (isinstance(array, ParseResults) == True 
                and self._VALUE_TYPE not in array):
                self._extractObjectType(array)
                self._extractArrayType(array)
                #parseResults[key][self._VALUE_DEFINED] = array
                
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
        #self._extractObjectType(self._modelInfo)
        self._extractArrayType(self._modelInfo)
       

    def _validate(self, parseResults, jsonObject, verifyExtendedKey=False):
        """Validates recursively the jsonObject against the parse results"""
        modelKeySet = set(parseResults.keys())
        objectKeySet = set(jsonObject.keys())
        
        # check for keys that extended key, keys in jsonObject but not in 
        # the model, the should follow the format of extended.
        if verifyExtendedKey == True:
            for key in objectKeySet-modelKeySet:
                if self.EXTENSION_VAR.match(key) is None:
                    raise ObjectModelParseException(
                             "Key '"+key+"' not present in model spec.")
        
        # Check for key that not in object but in the model and make sure t
        # that they are not required value.
        for key in modelKeySet - objectKeySet:
            if self._modelInfo[key].isRequired == True:
                raise ObjectModelParseException(
                        "Missing required key '"+key+"':\n\n"+
                        self._modelInfo[key][self._DESCRIPTION]+"\n\n")
        
        #Now check the key that are in both for type and value verification.
        for key in modelKeySet.intersection(objectKeySet):
            if isinstance(self._modelInfo[key], ParseResults) == False:
                continue
            
            #Get the description if there is any for the key.
            description = ""
            if self._DESCRIPTION in self._modelInfo[key].keys():
                description =  self._modelInfo[key][self._DESCRIPTION]
            
            #Check for correct type.
            if (self._VALUE_TYPE in self._modelInfo[key].keys() and 
               isOfJSONType(jsonObject[key], self._modelInfo[key].type) == False):
                raise ObjectModelParseException(
                    "Value for '"+key+"' is of wrong type, spec defines '"+key+
                    "' of type "+self._modelInfo[key][self._VALUE_TYPE]+"\n"+
                    description+"\n\n")
            
            
            #Check for matching default value
            if (self._VALUE_DEFINED in self._modelInfo[key].keys() and
                self._modelInfo[key][self._VALUE_DEFINED] != jsonObject[key]):
                raise ObjectModelParseException(
                    "Mismatch value for '"+key+"' expecting '"+
                    self._modelInfo[key][self._VALUE_DEFINED]+
                    "'\n\n:"+description+"\n\n")
                    
            #Check for value range.
            if (self._VALUE_RANGE in self._modelInfo[key].keys() and
               jsonObject[key] not in self._modelInfo[key][self._VALUE_RANGE]):
                raise ObjectModelParseException(
                    "Invalid value for'"+key+"'expecting one of:\n '"+
                    str(self._modelInfo[key][self._VALUE_RANGE])+
                    "'\n\n:"+description+"\n\n")
            
            if (self._modelInfo[key].type == 'array' or 
                self._modelInfo[key].type == 'object'):
                self._validate(self._modelInfo[key], jsonObject[key]+"\n\n")
    
    def _getModelInfo(self):
        self._extractData()
        return self._modelInfo
    
    
    
    modelInfo = property(_getModelInfo, None, None, None)
    
    def asJSON(self):
        """Transforms the parsed model to a valid JSON representation."""
        
        def parseResultsToDict(parseResults):
            if(parseResults is None or (isinstance(parseResults, ParseResults)== False)):
                return parseResults
            
            dictionary = parseResults.asDict()
            #Go down to each value and convert them to dictionary.
            for key in dictionary.keys():
                dictionary[key] = parseResultsToDict(dictionary[key]) 
            
            return dictionary
    
        return json.dumps(parseResultsToDict(self._modelInfo), indent=4)
    
   
    def validate(self, jsonObjectString):
        """Validates a JSON object string against the data model"""
        jsonObject = json.loads(jsonObjectString)
        self._validate(self._modelInfo, jsonObject, verifyExtendedKey=True)
        
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
    from os import path
    
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
    
    if options.source is not None:
        sourceString = ''
        #check to see if source is file path by the check if the file exist.
        if path.exists(options.source):
            sourceString = getFileString(options.source)
        else:
            sourceString = options.source
            
        model.validate(sourceString)
    
    