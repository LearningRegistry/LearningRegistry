#!/usr/bin/python

#    Copyright 2011 Lockheed Martin

'''
Script to parse Learning registry data model and validate JSON objects against
the parse models.

Created on Feb 15, 2011

@author: John Poyau
'''

import re, codecs, json, logging
from pyparsing import *
from os import path

log = logging.getLogger(__name__)

def getFileString(filename):

    # Use codecs to open the file as unicode encoded.
    file = codecs.open(filename, encoding='utf-8')
    fileString = file.read()
    file.close()

    # Remove the optional X_xxx enxtesion variable from the file string.   
    fileString = re.sub(r'\s+"X_xxx.*', '', fileString)
    
    # Replace the unicode quotation marks with plain one.
    fileString = re.sub(u"\u201c|\u201d", '"', fileString)

    return fileString

def getString(originalText, location, tokens):
    return "".join(tokens)

class ObjectModelParseException(Exception):
    """Shell exception class for model spec parsing exception"""
    pass

class SpecValidationException(Exception):
    """Shell exceptoin class model spec validition errors"""
    pass


def isOfSpecType(obj, type,elementType=None):
    if type == 'string':
        return (isinstance(obj, str) or
                     isinstance(obj, unicode))
    elif type == 'integer':
        return (isinstance(obj, int) or 
                     isinstance(obj, long))
    elif type == 'number':
        return (isinstance(obj, float) or
                isinstance(obj, int) or
                isinstance(obj, long))
    elif type == 'boolean':
        return isinstance(obj, bool)        
    elif type =='array':
        if (isinstance(obj, list) or isinstance(obj, tuple)):
            correct = True
            if elementType is not None:
                for element in obj:
                    correct = correct and isOfSpecType(element,elementType)
            return correct
        return False
    elif type == 'object':
        return isinstance(obj, dict)
    
    return False
    
        
class ModelParser(object):
        
    
    # Define some string constants
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
    _IS_REQUIRED_IF = 'isRequiredIf'
    _DESCRIPTION = 'description'
    _ARRAY_ELEMENT_TYPE = 1
    _SPEC_DATA_TYPES =  ['string', 'boolean', 'number', 'integer',  'array', 'object']
    
    # Define pyparsing variables.
    VAR = Regex('[A-Za-z0-9_.]+')
    INGORE_SPACE = Suppress(ZeroOrMore(White()))
    
    # Format of extension properties.
    EXTENSION_REGEX= re.compile('^X_')
    
    # The quote has to be a regular expression to deal with unicode 
    # open and close quotation marks.
    QUOTE = Regex('["'+unichr(0x201c)+unichr(0x201d)+']')
    
    NAME = INGORE_SPACE+Suppress(QUOTE)+VAR+Suppress(QUOTE)+INGORE_SPACE
    NAME.setParseAction(getString)
    
    TYPES =  oneOf(_SPEC_DATA_TYPES)
    TYPES.setParseAction(getString)
    QUOTED_TYPES = (Suppress(QUOTE)+TYPES+Suppress(QUOTE)) 
       
    SPEC_DATA_TYPES = QUOTED_TYPES|TYPES
    SPEC_DATA_TYPES.setParseAction(getString)
    
    
    OBJECT_START = Suppress('{')
    OBJECT_END = Suppress('}')
    COMMENT_START= '//'
    
    COMMENT = Combine(OneOrMore(White()+COMMENT_START+SkipTo(LineEnd())))
        
    KEY = NAME+Suppress(':')
    KEY.setParseAction(getString)
    
    # Forward definition of object since a value can be an object.
    OBJECT = Forward()
    
    ARRAY = '['+(QUOTED_TYPES.setParseAction(getString).setResultsName(_VALUE_TYPE)|\
                (Optional(COMMENT_START+FollowedBy(OBJECT)).setResultsName(_VALUE_COMMENT)
                +OBJECT))+']'
    
    
    # Inline value are just string inside of a bracket.
    INLINE_VALUE = OBJECT_START + \
                originalTextFor(OneOrMore(Word(alphanums)))+OBJECT_END
    INLINE_VALUE.setParseAction(getString)
                
    VALUE = (SPEC_DATA_TYPES.setResultsName(_VALUE_TYPE)
             |NAME.setResultsName(_VALUE_DEFINED)
             |ARRAY.setResultsName(_VALUE_TYPE_ARRAY)
             |INLINE_VALUE.setResultsName(_VALUE_TYPE_INLINE)
             |OBJECT.setResultsName(_OBJECT)
            )+ \
             Suppress(','|FollowedBy(COMMENT_START|OBJECT_END))
    
    # This parser will look for fixed vocabulary strings which signals that the
    # property has defined range of values.
    VALUE_RANGE = Combine(Suppress(Regex(u'fixed\s+vocabulary\s+'))+\
              Regex(r'\[[^]]+\]')).setResultsName(_VALUE_RANGE)

    REQUIRED = Keyword('required')
    IF = Keyword('if')
    # The field is really required if it is not followed by if.
    IS_REQUIRED = REQUIRED+~FollowedBy(IF)
    IS_REQUIRED.setParseAction(lambda s, p, t: True)
    
    IS_REQUIRED_IF = Suppress(REQUIRED+IF)+NAME
    
    IS_REQUIRED_IF.setParseAction(getString)
    
    IS_IMMUTABLE = Keyword('immutable')
    IS_IMMUTABLE.setParseAction(lambda s, p, t: True)
    
    # Parser that extracts any useful information from the comments.
    COMMENT_INFO = (Optional(SkipTo(VALUE_RANGE)+
                            VALUE_RANGE.setResultsName(_VALUE_RANGE))+\
                    Optional(SkipTo(IS_REQUIRED_IF)+
                             IS_REQUIRED_IF.setResultsName(_IS_REQUIRED_IF))+\
                    Optional(SkipTo(IS_REQUIRED)+
                            IS_REQUIRED.setResultsName(_IS_REQUIRED))+\
                    Optional(SkipTo(IS_IMMUTABLE)+
                           IS_IMMUTABLE.setResultsName(_IS_IMMUTABLE))
                    ).setResultsName(_VALUE)
                    

    
    PROPERTY = \
                Group(
                            (KEY.setResultsName(_KEY)+
                            COMMENT.setResultsName(_KEY_COMMENT)+
                            VALUE.setResultsName(_VALUE)+
                            COMMENT.setResultsName(_VALUE_COMMENT)
                            )
                            |
                            (KEY.setResultsName(_KEY)+
                             VALUE.setResultsName(_VALUE)+
                            COMMENT.setResultsName(_VALUE_COMMENT)
                            )
                            |
                            (KEY.setResultsName(_KEY)+
                            VALUE.setResultsName(_VALUE)
                            )
                        ) 
                           
    PROPERTY.setResultsName(_PROPERTY)
    

    OBJECT << (OBJECT_START+
                ZeroOrMore(Dict(PROPERTY.setResultsName(_PROPERTY)))+
                OBJECT_END
               ).setResultsName(_OBJECT)
    
   
            
    
    def __init__(self, modelSpec):
        """Class that parses data models from the spec for object validation.
          modelSpec String represention of a model based on Dan Rehak JSON like
                  format. Or Full path of a file that contains Dan Rehak JSON like
                   data model"""
        
        self._fileString = None
        self._modelName = None
        self._parseResults = None

        # The _modelInfo is a copy of the _parseResults where some duplicate
        # information has been remove.
        self._modelInfo = None
        self._fileString = modelSpec
            
        if path.exists(modelSpec):
            self._fileString = getFileString(modelSpec)
      
        # Parse the model
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
            # Remove the _KEY_COMMENTS from list of keys.
            parseResults.pop(self._KEY_COMMENT)
            
        if self._VALUE_COMMENT in parseResults.keys():
            commentString = commentString + parseResults[self._VALUE_COMMENT]
            parseResults.pop(self._VALUE_COMMENT)

        if len(commentString) == 0:
            return 
        
        # Clean up the comment string, remove the // and extra spaces.
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
            
            # See if there is any comment to extract info from.
            if self._VALUE_COMMENT in parseResults[key].keys():
                commentString = parseResults[key][self._VALUE_COMMENT]
                # Parse the comments for any additional info
                commentInfo = self.COMMENT_INFO.parseString(commentString)
                
                # For some reason pyparsing parseAction does no like to return
                # a list. So look for any valueRange value, eval to it a list,
                # and convert the list to a tuple
                if self._VALUE_RANGE in commentInfo.keys():
                    rangeString = commentInfo[self._VALUE_RANGE]
                    # Clean the range string, remove extra space and errand char
                    rangeString = re.sub(r"\s+|/", ' ', rangeString)                     
                    commentInfo[self._VALUE_RANGE] = tuple(eval(rangeString))
                
                # Cleanup comment info before merging
                self._cleanup(commentInfo)

                # Merge any info extracted from the comment.
                parseResults[key] = parseResults[key] + commentInfo
                # Put the comments to a desciption key.
                self._commentsToDescription(parseResults[key])
                
        return parseResults
        
    
    def _extractObjectType(self, parseResults):
        """Futher parses and cleans values of type object"""

        obj = None
        for key in parseResults.keys():
            if self._VALUE_TYPE_INLINE in parseResults[key].keys():
                objobject = parseResults[key][self._VALUE_TYPE_INLINE]
                parseResults[key][self._VALUE_TYPE] = 'object'
                # Remove the old inline key.
                parseResults[key].pop(self._VALUE_TYPE_INLINE)
                
            # If the object is of type ParseResults process it futher to 
            # extract any comments or array info
            if isinstance(obj, ParseResults) == True:
                self._extractObjectType(obj)
                self._extractArrayType(obj)
              
    
    def _extractArrayType(self, parseResults):
        """Futher parse and clean values of type array"""
        array = None
        for key in parseResults.keys():
            if isinstance(parseResults[key], ParseResults) == False:
                continue
            
            if self._VALUE_TYPE_ARRAY in parseResults[key].keys():
                array = parseResults[key][self._VALUE_TYPE_ARRAY]
                parseResults[key][self._VALUE_TYPE] = 'array'
                # Remove the old value type array key.
                parseResults[key].pop(self._VALUE_TYPE_ARRAY)
            # If the object is parse result process it futher to 
            # extract comments or array info
            if (isinstance(array, ParseResults) == True 
                and self._VALUE_TYPE not in array):
                self._extractObjectType(array)
                self._extractArrayType(array)
               
                
    
    def _extractIsRequiredIf(self, parseResults):
        """ Extracts info for conditionally required property"""
        valueRanges = {}
        
        # Get all the keys with value range and save them for later to seach 
        # for conditionally required value.
        for key in parseResults.keys():
            if (isinstance(parseResults[key], ParseResults) 
                and self._VALUE_RANGE in parseResults[key].keys()):
                valueRanges[key] = parseResults[key][self._VALUE_RANGE]
                
        # Deals with conditionally required value. if we have one look for it
        # in the value range and record the property that makes it required.
        for key in parseResults.keys():
            if isinstance(parseResults[key], ParseResults) == True:
                self._extractIsRequiredIf(parseResults[key])
            else:
                continue
            
            if self._IS_REQUIRED_IF in parseResults[key].keys():
                for k in valueRanges.keys():
                    if parseResults[key][self._IS_REQUIRED_IF] in valueRanges[k]:
                        # We should check to see if the value is also in the
                        # range of some other key, meaning that the requireif is 
                        # already set to dictionary if so raise an exception.
                        if isinstance(parseResults[key][self._IS_REQUIRED_IF], 
                                      dict) == True:
                            raise(ObjectModelParseException( 
                                    "Cannot parse comment about required if: "+
                                    parseResults[key][self._DESCRIPTION]))
                                    
                        parseResults[key][self._IS_REQUIRED_IF] = \
                                    {k:parseResults[key][self._IS_REQUIRED_IF]}
                
                # Raise an exception if we not could find the property that
                # that makes the property required.
                if isinstance(parseResults[key][self._IS_REQUIRED_IF], dict)== False:
                    raise(ObjectModelParseException( 
                            "Cannot find key for parsed comment required if: "+
                            "key: "+key+"\nComment: \n"+
                            parseResults[key][self._DESCRIPTION]))
                
    
    def _extractData(self):
        """Parses the spec data model"""
        
        # Don't do anything if the data is already parsed.
        if self._parseResults is not None and self._modelInfo is not None:
            return
        
        self._parseResults =  ModelParser.OBJECT.parseString(self._fileString)
        # Get the name of the model.    
        if 'doc_type' in self._parseResults.keys():
            self._modelName = self._parseResults.doc_type.valueDefault
        
        self._modelInfo = self._parseResults.copy()
        try:
            self._modelName = self._modelInfo.doc_type.value
        except Exception as e:
            log.info("Cannot get document type: "+str(e))
            
        
        self._cleanup(self._modelInfo)
        self._extractCommentInfo(self._modelInfo)
        self._extractIsRequiredIf(self._modelInfo)
        #self._extractObjectType(self._modelInfo)
        self._extractArrayType(self._modelInfo)
        
    def _validateConditionalField(self, fieldName, value, modelProp, jsonObject):
        """Validates conditionally required property"""
        
        if self._IS_REQUIRED_IF not in modelProp.keys() or \
           fieldName not in jsonObject.keys():
                 return

        # Get description for the the file if there is any.
        description = ''
        if self._DESCRIPTION in modelProp.keys():
            description = modelProp[self._DESCRIPTION]+"\n\n"

        #The dictionary has only one item.
        conditionalKey = modelProp[self._IS_REQUIRED_IF].keys()[0]
        conditionalValue = modelProp[self._IS_REQUIRED_IF][conditionalKey]
        conditionalProp = jsonObject.get(conditionalKey)
        
        # Make sure that if a conditionally required key is present its
        # condition is met.
        if self._IS_REQUIRED_IF in modelProp.keys():
            #The dictionary has only one items.
            conditionalKey =  modelProp[self._IS_REQUIRED_IF].keys()[0]
            conditionalValue =  modelProp[self._IS_REQUIRED_IF][conditionalKey]
            conditionalProp = jsonObject[conditionalKey]
            if conditionalValue != conditionalProp:
                raise SpecValidationException(
                "Conditionally required property '"+fieldName +
                "' is present without meeting the required condition. '" +
                str(conditionalKey)+"' must be '"+str(conditionalValue)+
                "' yet it is set to '"+str(conditionalProp)+
                "'\n\n"+description)
                
            # If the propety field is required conditionally based on another 
            # property value check to see if that property value is present.
            if (conditionalKey in jsonObject.keys() and 
                conditionalProp == conditionalValue and
                 fieldName not in jsonObject.keys() ):
                raise SpecValidationException(
                        "Key '"+fieldName+"' is required if '"+str(conditionalKey) +
                        "' is set to '"+str(conditionalValue)+"' :\n\n"+description)

        
    def _validateField(self, fieldName, value,  modelProp):
        """Validates that the field named key conforms to the spec model for the key"""
    
        # Get description for the the file if there is any.        
        description = ''
        if self._DESCRIPTION in modelProp.keys():
            description = modelProp[self._DESCRIPTION]+"\n\n"
        def createTest():
            if modelProp[self._VALUE_TYPE] == 'array':
                return isOfSpecType(value, modelProp[self._VALUE_TYPE],modelProp[self._ARRAY_ELEMENT_TYPE])    
            else:    
                return isOfSpecType(value, modelProp[self._VALUE_TYPE])                    
        # Check for correct type.
        if (self._VALUE_TYPE in modelProp.keys() and  createTest() == False):
            raise SpecValidationException(
                "Value for '"+fieldName+"' is of wrong type, spec defines '"
                +fieldName+"' of type "+
                modelProp[self._VALUE_TYPE]+"\n\n"+description)
                
        #Check that required string are not empty.
        if (self._IS_REQUIRED in modelProp.keys() and 
            isOfSpecType(value, 'string') and 
            len(value.strip()) == 0):
                raise SpecValidationException(
                    "Required value for '"+fieldName+"' cannot be an empty string\n\n"
                    +description)
                    
         # Check for matching defined value
        if (self._VALUE_DEFINED in modelProp.keys() and
            modelProp[self._VALUE_DEFINED] != value):
            raise SpecValidationException(
                "Mismatch value for '"+fieldName+"' expecting '"+
                modelProp[self._VALUE_DEFINED]+"' instead of '"+str(value)+
                "'\n\n"+description)
                    
        # Check for value range.
        if (self._VALUE_RANGE in modelProp.keys() and
           value not in modelProp[self._VALUE_RANGE]):
            raise SpecValidationException(
                "Invalid value for'"+fieldName+"'expecting one of:\n '"+
                str(modelProp[self._VALUE_RANGE]) +"' instead of '"+str(value)+
                "'\n\n:"+description)
        
      
    def _validate(self, parseResults, jsonObject, validateExtensionField=False):
        """Validates recursively the jsonObject against the spec model"""
        modelKeySet = set(parseResults.keys())
        objectKeySet = set(jsonObject.keys())
    
        # Check for keys that are extension properties and ensure that they
        # comform to the spec extension variable format.
        if validateExtensionField  == True:
            for key in objectKeySet-modelKeySet:
                if self.EXTENSION_REGEX.match(key) is None:
                    raise SpecValidationException(
                             "Key '"+key+"' not present in model spec.")
        
        # Check for key that not in object but in the model and make sure
        # that they are not required value.
        for key in modelKeySet - objectKeySet:
            modelProp = parseResults[key]
            # Get the description if there is any for the property.
            description = ""
            if self._DESCRIPTION in modelProp.keys():
                description =  modelProp[self._DESCRIPTION]
                
            if modelProp.isRequired == True:
                raise SpecValidationException(
                        "Missing required key '"+key+"':\n\n"+
                        description+"\n\n")
            self._validateConditionalField(key, None, modelProp, jsonObject) 
        
        # Now check that key that are in both jsonobject and model spec
        # for type and defined value verification.
        for key in modelKeySet.intersection(objectKeySet):
            
            modelProp = parseResults[key]
            value = jsonObject[key]
            
            if isinstance(modelProp, ParseResults) == False:
                continue
            self._validateConditionalField(key, value, modelProp, jsonObject)
            self._validateField(key, value, modelProp)
            
            # Validate any sub object.
            if (modelProp.type == 'object'):
                self._validate(modelProp, objectProp)
    

    def _getModelInfo(self):
        self._extractData()
        return self._modelInfo
    
    def _getDocVersion(self):
        if 'doc_version' in self.modelInfo:
            return self.modelInfo.doc_version.value
        return None
    
    modelInfo = property(_getModelInfo, None, None, None)
    modelName = property(lambda self: self._modelName, None, None, None)
    docVersion = property(_getDocVersion, None, None, None)
    
    def asJSON(self):
        """Transforms the parsed model to a valid JSON representation."""
        
        def parseResultsToDict(parseResults):
            if(parseResults is None or 
               (isinstance(parseResults, ParseResults)== False)):
                return parseResults
            
            dictionary = parseResults.asDict()
            # Go down to each value and convert them to a dictionary.
            for key in dictionary.keys():
                dictionary[key] = parseResultsToDict(dictionary[key]) 
            
            return dictionary
    
        return json.dumps(parseResultsToDict(self._modelInfo), indent=4)
    
    def validateField(self, fieldName, value, jsonObject):
        """Veryfies that a field conforms the the specs."""
        
        # Check for keys that are extension properties and ensure that they
        # comform to the spec extension variable format.
        if (fieldName not in  self._modelInfo.keys()  and
             self.EXTENSION_REGEX.match(fieldName) is None):
                    raise SpecValidationException(
                             "Key '"+fieldName+"' not present in model spec.")
        
        modelProp = self._modelInfo[fieldName]                    
        self._validateField(fieldName, value, modelProp)
        self._validateConditionalField(fieldName, value, modelProp, jsonObject)
       
        if modelProp.get(self._VALUE_TYPE)=='object':
           self._validate(modelProp, value)
       
    def validate(self, jsonObjectString):
        """Validates a JSON object string against the data model"""
        jsonObject = {}
        if isinstance(jsonObjectString, dict):
            jsonObject = jsonObjectString
        else:
            jsonObject = json.loads(jsonObjectString)
        
        self._validate(self._modelInfo, jsonObject, validateExtensionField=True)
        return jsonObject
 
# Parser that extracts object data models from a spec file.       
SPEC = OneOrMore(Suppress(SkipTo(ModelParser.OBJECT))+
                originalTextFor(ModelParser.OBJECT))
                
def extractModelsFromSpec(specFile, destDir='./models/'):
    """Extract all models from the spec file """
    
    # Add the trailing slash to the directory name.
    print("Destination directory: "+destDir)
    if path.exists(destDir) == False:
        os.makedirs(destDir)
    
    specFileString = getFileString(specFile)
    dataModels = SPEC.parseString(specFileString)
    for model in dataModels:
        # Look for the doc_type. object string without a doc_type are not
        # considered as models they are ignored.
        modelName = re.search('"doc_type"\s*:\s*"(?P<name>[^"]+)"', model)
        if modelName is None:
            continue
        modelFilePath = path.join(destDir,modelName.group('name'))
        print("Create data model spec file: "+modelFilePath+"\n") 
        modelFile = codecs.open(modelFilePath, encoding='utf-8', mode='w')               
        modelFile.write(model)
        modelFile.close()
        
        

if __name__== "__main__":
    from optparse import OptionParser
    import os
    
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filepath", 
                      help="The full path of the data model spec definition.",  metavar="FILE")
                    
    parser.add_option("-s", "--string", dest="string",  help="String representation of the data model spec definition")
                
    parser.add_option("-j", "--json", dest="json", action = "store_true", 
                      default=False,  help="Show a json representation of data model spec.")
                    
    parser.add_option("-v", "--validate", dest="source",  help="""Validates a JSON object against the spec data model
                            The source JSON object can be a file or a string 
                            representation of the JSON object.
                            """
                        )
    parser.add_option("-e", "--extract", dest="specFile",  help="extracts data models from the spec file.",  metavar="FILE")
    
    parser.add_option("-d", "--destination", dest="modelDestination",  help="""Destination path to put data model file specs 
                            that are extracted from the main spec.""")


    (options, args) = parser.parse_args()
    
    model = None
    
    if options.filepath is not None:
        model = ModelParser(options.filepath)
        
    elif options.string is not None:
        model = ModelParser(options.string)
        
    if (((options.filepath is not None) or
         (options.string is not None)) and
         (model is None)):
        print("Failed to parse data model spec.")
        exit()
    
    if options.json == True:
        print model.asJSON()
    
    if options.source is not None:
        sourceString = ''
        # Check to see if source is a file path by checking if the file exists.
        if path.exists(options.source):
            sourceString = getFileString(options.source)
        else:
            sourceString = options.source
            
        model.validate(sourceString)
        print("\n\n Object conforms to "+model.modelName+" model spec")
        
    if options.modelDestination is not None and options.specFile is not None:
        print("Spec file: "+options.specFile+"\n")
        print("Data Model spec Destination Dir: "+options.modelDestination+"\n")
        extractModelsFromSpec(options.specFile, options.modelDestination)        
    
    
