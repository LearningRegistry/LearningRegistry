#!/usr/bin/python
from LR.lr.lib import ModelParser
from LR.lr.lib.model_parser import getFileString


if __name__== "__main__":
    from optparse import OptionParser
    from os import path
    import os
    
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
    parser.add_option("-e", "--extract", dest="specFile",
                      help="extracts data models from the spec file.",
                      metavar="FILE")
    
    parser.add_option("-d", "--destination", dest="modelDestination",
                      help="""Destination path to put data model file specs 
                            that are extracted from the main spec.""")


    (options, args) = parser.parse_args()
    
    model = None
    
    if options.filepath is not None:
        model = ModelParser(filePath=options.filepath)
        
    elif options.string is not None:
        model = ModelParser(string = options.string)
        
    if (((options.filepath is not None) or
         (options.string is not None)) and
         (model is None)):
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
        print("\n\n Object conforms to "+model.modelName+" model spec")
        
    if options.modelDestination is not None and options.specFile is not None:
        print("Spec file: "+options.specFile+"\n")
        print("Data Model spec Destination Dir: "+options.modelDestination+"\n")
        extractModelsFromSpec(options.specFile, options.modelDestination)        
    
    