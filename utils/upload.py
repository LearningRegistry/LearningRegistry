#!/usr/bin/env python
import urllib2,os,json,codecs
import ConfigParser
from random import choice
import argparse
from LRSignature.sign.Sign import Sign_0_21
signer = None
import time
parser = argparse.ArgumentParser(description='Sign files and upload to Learning Registry')
parser.add_argument('--key', help='PGP Private Key ID')
parser.add_argument('--key-location', help='Location the PGP Public Key can be downloaded from')
parser.add_argument('--passphrase', help='Passphrase for PGP Private Key', default=None)
parser.add_argument('--gpgbin', help='Path to GPG binary', default="gpg")
parser.add_argument('--publish-url', help='Learning Registry Node publish url. Overrides publish_url in [upload] from configuration file', default=None)
parser.add_argument('--data-dir', help='Directory of source LR Data Envelopes. Overrides root_path in [upload] from configuration file"', default=None)
parser.add_argument('--lr-test-data', help='Publish as lr test data, default is True', default="False")
parser.add_argument('--config', help='Configuration file, default is "testconfig.ini"', default="testconfig.ini")
parser.add_argument('--user',help="Username for basic auth", default=None)
parser.add_argument('--passwd',help="Password for basic auth", default=None)
args = parser.parse_args()
if args.key is not None and args.key_location is not None:
    signer = Sign_0_21(privateKeyID=args.key ,publicKeyLocations=[args.key_location], passphrase=args.passphrase, gpgbin=args.gpgbin)
_config = ConfigParser.ConfigParser()
_config.read(args.config)
#root_path = _config.get("upload", "root_path")
#publish_url = _config.get("upload", "publish_url")
lr_test_data = args.lr_test_data.lower() in ["true", "t", "yes" "1"]

if args.publish_url != None:
    publish_url = args.publish_url

if args.data_dir != None:
    root_path = args.data_dir

def upload_files(docs):
  try:
    data = json.dumps({'documents':docs})
    if args.user is not None and args.passwd is not None:
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, publish_url, args.user, args.passwd)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)
    request = urllib2.Request(publish_url,data,{'Content-Type':'application/json; charset=utf-8'})
    response = urllib2.urlopen(request)
    with open('error.html','a') as out:
      out.write(response.read())
      out.write('\n')	
  except urllib2.HTTPError as er:
    with open('error.html','a') as out:
      out.write(er.read())
    print 'error'
    
def set_test_key(data, remove=True):
    rmcount = 0
    for item in data["keys"]:
        if item == "lr-test-data":
            rmcount += 1
    if remove:
        while rmcount > 0:
            try:
                data["keys"].remove("lr-test-data")
            except:
                pass
            rmcount += -1
    elif not remove and rmcount == 0:
        data["keys"].append("lr-test-data")
    return data
        
def process_files():
    documents=[]
    for root,dirs, files in os.walk(root_path):
        for fname in files:
            print fname
            file_path = os.path.join(root,fname)
            with codecs.open(file_path,'r+', 'utf-8-sig') as f:
                data = json.load(f)        
            
            if not lr_test_data and data.has_key("keys"):
                data = set_test_key(data)
            else:
                data = set_test_key(data, remove=False)
            
            if signer is not None: 
                print 'signing {0}'.format(fname)           
                data = signer.sign(data)
            documents.append(data)
            if len(documents) >= 10:
                upload_files(documents)
                documents=[]
                time.sleep(1)
def main():
    process_files();
if __name__ == '__main__':
    main()
