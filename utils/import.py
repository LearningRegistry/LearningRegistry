import urllib2, os, libxml2, json

rootPath = 'C:\\Documents and Settings\\admin\\Desktop\\json\\20110228_eun_MDlre4_LR_0_10_0_100'
publish_url = 'http://12.109.40.15/publish'
docs = []
write_to_file = False
output_file_path = 'C:\\Documents and Settings\\admin\\Desktop\\json\\20110228_eun_MDlre4_LR_0_10_0_180000'
if os.path.exists(os.path.join(rootPath,'error.html')):
  #delete old error log file if it exists
  os.remove(os.path.join(rootPath,'error.html'))
#iterate through all metadata docs 
def process_docs(count):
  if(write_to_file):
    if not os.path.exists(output_file_path):
      os.mkdir(output_file_path)
    for i in range(0,len(docs)):
      if os.path.exists(os.path.join(output_file_path,'2011-02-28Metadata'+str(i + count)+'.json')):
        with open(os.path.join(output_file_path,'2011-02-28Metadata'+str(i + count)+'.json'),'w') as f:
	      f.write(json.dumps(docs[i]))
  else:
    #convert to JSON
    data =json.dumps({'documents':docs})
    try:
      #use a post to send data to the learning registry
      request = urllib2.Request(publish_url,data,{'content-type':'text/json'})
      response = urllib2.urlopen(request)
    except urllib2.HTTPError as err:
      #if something bad happened dump the error to an html file so it can be displayed in a browser
      with open(os.path.join(rootPath,'error.html'),'w') as f:
        for line in err.readlines():
          f.write(line)
      output = os.path.join(rootPath,'error.html')
      print 'see file ' + output
doc_count = 0
for childDir in os.listdir(rootPath):
  childPath = os.path.join(rootPath,childDir)
  for file in os.listdir(childPath):  
    #use xpath to pull relevant fields out of the xml doc
    doc = libxml2.parseFile(os.path.join(childPath , file))
    context = doc.xpathNewContext()
    context.xpathRegisterNs('oai','http://www.openarchives.org/OAI/2.0/')
    context.xpathRegisterNs('ims','http://www.imsglobal.org/xsd/imslorsltitm_v1p0')
    context.xpathRegisterNs('lom','http://ltsc.ieee.org/xsd/LOM')
    #we only need to content of the xml nodes	
    location = context.xpathEval("//ims:expression/ims:manifestation/ims:item/ims:location/ims:uri/text()")[0].getContent()
    doc.freeDoc()  
    context.xpathFreeContext()
    #read the raw XML as a UTF-8 string
    with open(os.path.join(childPath,file),'r+') as f:
      read_data = json.dumps(f.read())
    doc = {
           "doc_type":        "resource_data",
           "doc_version":        "0.10.0",
           "active":        True,
           "resource_data_type":    "metadata",
           "submitter_type":    "anonymous",
           "update_timestamp":    "01/12/2011",
           "create_timestamp":    "01/12/2011",		   
           "submitter":        "test data set submitter",
           "submission_TOS":    "http://www.learningregistry.org/tos-v1-0.html",
           "resource_locator":    location,
           "keys":        ["EUN", "LOM", "test data"],
           "payload_placement":    "inline",
           "payload_schema":    ["LODE, LOM"],
           "resource_data": read_data,
		   'publishing_node': 'nsdl'
          }  
    docs.append(doc)
    if len(docs) > 1000:
      process_docs(doc_count)
      doc_count = doc_count + len(docs)
      docs = []
