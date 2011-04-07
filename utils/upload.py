#!/usr/bin/python
import urllib2,os,json
import ConfigParser
from random import choice
_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
root_path = _config.get("upload", "root_path")
publish_url = _config.get("upload", "publish_url")
publish_urls = ['http://lrdev1.learningregistry.org/publish','http://lrdev2.learningregistry.org/publish','http://lrdev3.learningregistry.org/publish']
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
  publish_url = choice(publish_urls)
  file_path = os.path.join(root_path,file)
  with open(file_path,'r+') as f:
    data = json.load(f)
  documents.append(data)
  if len(documents) >= 10:
    upload_files(documents)
    documents=[]
