import urllib2,os,json
import ConfigParser
root_path = 'C:\\Documents and Settings\\admin\\Desktop\\json\\20110228_eun_MDlre4_LR_0_10_0_180000'
publish_url = 'http://192.168.153.130/publish'

_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
root_path = _config.get("upload", "root_path")
publish_url = _config.get("upload", "publish_url")

documents=[]

def upload_files(docs):
  try:
    data = json.dumps({'documents':docs})
    request = urllib2.Request(publish_url,data,{'Content-Type':'application/json'})
    response = urllib2.urlopen(request)
    with open('error.html','a') as out:
      out.write(response.read())
      out.write('\n')	
  except urllib2.HTTPError as er:
    with open('error.html','a') as out:
      out.write(er.read())
    print 'error'
    
for file in os.listdir(root_path):
  file_path = os.path.join(root_path,file)
  with open(file_path,'r+') as f:
    data = json.load(f)
  documents.append(data)
  if len(documents) >= 10:
    upload_files(documents)
    documents=[]