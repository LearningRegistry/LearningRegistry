
import urllib2,os,json
root_path = '/home/wegrata/Downloads/test_data'
publish_url = 'http://localhost/publish'
documents=[]
def upload_files(docs):
  try:
    data = json.dumps({'documents':docs})
    request = urllib2.Request(publish_url,data,{'Content-Type':'application/json'})
    response = urllib2.urlopen(request)
    with open('error.html','w') as out:
      out.write(response.read())	
  except urllib2.HTTPError as er:
    with open('error.html','w') as out:
      out.write(er.read())

for file in os.listdir(root_path):
  file_path = os.path.join(root_path,file)
  with open(file_path,'r+') as f:
    data = json.load(f)
  documents.append(data)
  if len(documents) >= 99:
    upload_files(documents)
    documents=[]
