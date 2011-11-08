import urllib2, os,  json, ConfigParser, argparse
from lxml import etree
import codecs
rootPath = '/home/wegrata/test'
publish_url = 'http://lrtest02.learningregistry.org/publish'
docs = []
write_to_file = False
output_file_path = '/dev/null'

_parser = argparse.ArgumentParser(description='Convert RAW EUN XML Metadata to LR Envelopes')
_parser.add_argument('--config', help='INI configuration file. See testconfig.ini.sample', default='testconfig.ini')
args = _parser.parse_args()

_config = ConfigParser.ConfigParser()
_config.read(args.config)

#rootPath = _config.get("import", "root_path")
#output_file_path = _config.get("import", "out_path")
#write_to_file = _config.get("import", "write_to_file").lower() in ["true"]

width  = 0
count = 0
if os.path.exists(os.path.join(rootPath,'error.html')):
  #delete old error log file if it exists
  os.remove(os.path.join(rootPath,'error.html'))
#iterate through all metadata docs 
def process_docs(count):
  print write_to_file
  if(write_to_file):
    if not os.path.exists(output_file_path):
      os.mkdir(output_file_path)
    fmt = '2011-02-28Metadata%06d.json'
    for i in range(0,len(docs)):
      if os.path.exists(output_file_path):
          
          outFile = os.path.join(output_file_path,fmt % count)
          count +=1
          if os.path.exists(outFile) == True:
              os.remove(outFile)
                                     
          with codecs.open(outFile,'w', 'utf-8-sig') as f:
              f.write(json.dumps(docs[i], sort_keys=True, indent=4))
              print outFile
            
  else:
    #convert to JSON
    data =json.dumps({'documents':docs})
    try:
      #use a post to send data to the learning registry
      request = urllib2.Request(publish_url,data,{'content-type':'text/json'})
      response = urllib2.urlopen(request)
      print response.read()
    except urllib2.HTTPError as err:
      #if something bad happened dump the error to an html file so it can be displayed in a browser
      with open(os.path.join(rootPath,'error.html'),'w') as f:
        for line in err.readlines():
          f.write(line)
      output = os.path.join(rootPath,'error.html')
      print 'see file ' + output
      
def parse_raw_docs():
    global docs      
    doc_count = 0
    for root, dirs,files in os.walk(rootPath):
        for fname in files:
            rootFile = os.path.join(root,fname)
        #  for file in os.listdir(childPath): use xpath to pull relevant fields out of the xml doc
            with open(rootFile,'r') as f:
                data = f.read()                        
            xmldoc = etree.fromstring(data)
            namespaces = {'lom':'http://ltsc.ieee.org/xsd/LOM'}
            #we only need to content of the xml nodes                
            location =  "http://hdl.handle.net/"
            keyTags = xmldoc.xpath("//lom:lom/lom:general/lom:keyword/lom:string/text()",namespaces=namespaces)
            keys = []
            for key in keyTags:
                keys.append(unicode(key))             

            #read the raw XML as a UTF-8 string
            doc = {
               "doc_type":              "resource_data",
               "doc_version":           "0.23.0",
               "active":                True,
               "resource_data_type":    "metadata",
               "resource_locator":      location,
               "keys":                  keys,
               "payload_placement":     "inline",
               "payload_schema":        ["LODE", "LOM"],
               "resource_data":         data,
               "identity": {
                            "submitter_type":   "agent",
                            "submitter":        "JKO",
                            "curator":          "ADL",
                            "owner":            "JFSC"
        #                        'signer':''
                },
               "TOS": {
                       "submission_TOS":        "http://www.learningregistry.org/tos/cc0/v0-5/"
                    },
                  }  
            docs.append(doc)
            if len(docs) > 1000:
                yield (doc_count, docs)
                doc_count = doc_count + len(docs)
                docs = []
        if len(docs) > 0:
            yield (doc_count, docs)
        

for (doc_count, batch) in parse_raw_docs():
    process_docs(doc_count)
