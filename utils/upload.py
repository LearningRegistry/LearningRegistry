#!/usr/bin/python
import urllib2,os,json,codecs
import ConfigParser
from random import choice
import argparse
from LRSignature.sign.Sign import Sign_0_21
signer = None
parser = argparse.ArgumentParser(description='Sign files and upload to Learning Registry')
parser.add_argument('--key', help='PGP Private Key ID')
parser.add_argument('--key-location', help='Location the PGP Public Key can be downloaded from')
parser.add_argument('--passphrase', help='Passphrase for PGP Private Key', default=None)
args = parser.parse_args()
if args.key is not None and args.key_location is not None:
    signer = Sign_0_21(privateKeyID=args.key ,publicKeyLocations=[args.key_location], passphrase=args.passphrase )
_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
root_path = _config.get("upload", "root_path")
publish_url = _config.get("upload", "publish_url")
publish_urls = ['http://lrdev1.learningregistry.org/publish','http://lrdev2.learningregistry.org/publish','http://lrdev3.learningregistry.org/publish']

def upload_files(docs):
  try:
    data = json.dumps({'documents':docs})
    request = urllib2.Request(publish_url,data,{'Content-Type':'application/json; charset=utf-8'})
    response = urllib2.urlopen(request)
    with open('error.html','a') as out:
      out.write(response.read())
      out.write('\n')	
  except urllib2.HTTPError as er:
    with open('error.html','a') as out:
      out.write(er.read())
    print 'error'
def process_files():
    documents=[]
    for file in os.listdir(root_path):
        file_path = os.path.join(root_path,file)
        with codecs.open(file_path,'r+', 'utf-8-sig') as f:
            data = json.load(f)        
        if signer is not None:            
            data = signer.sign(data)
        documents.append(data)
        if len(documents) >= 10:
            upload_files(documents)
            documents=[]
def main():
    process_files();
if __name__ == '__main__':
    main()
