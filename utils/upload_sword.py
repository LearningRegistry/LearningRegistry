#!/usr/bin/python
import urllib2
import os
import json
import ConfigParser
from random import choice
_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
root_path = _config.get("upload", "root_path")
publish_url = _config.get("upload", "sword_url")
publish_urls = ['http://node01.public.learningregistry.net/sword','http://node02.public.learningregistry.net/sword','http://node03.public.learningregistry.net/sword']
results = []
def upload_file(doc):
  try:
    data = json.dumps(doc)
    request = urllib2.Request(publish_url,data,{'Content-Type':'application/json'})
    response = urllib2.urlopen(request)
    result = response.read()
    print result
    results.append(result)
  except urllib2.URLError as er:
    print er
    print publish_url
  except urllib2.HTTPError as er:
    with open('error.html','a') as out:
      out.write(er.read())
    print publish_url
    print 'error'
    
for file in os.listdir(root_path):
  publish_url = choice(publish_urls)
  file_path = os.path.join(root_path,file)
  with open(file_path,'r+') as f:
    data = json.load(f)    
  upload_file(data)    
with open('results.xml', 'w') as output:
    output.write(str(results))
