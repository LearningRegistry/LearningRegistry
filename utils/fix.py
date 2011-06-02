#!/usr/bin/python
import os, json
import ConfigParser
_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
base_path = _config.get("fix", "root_path")
for file in os.listdir(base_path):
    changed = False
    file_path = os.path.join(base_path, file)
    with open(file_path,'r+') as f:
        data = json.load(f)
    data['doc_version'] = '0.21.0'
    if data.has_key('submitter'):
		changed = True
		del data['submitter']
    if data.has_key('submitter_type'):
		changed = True
		del data['submitter_type']		
    if data.has_key('identify'):
        del data['identify']
        changed = True
    if not data.has_key('identity'):
        changed = True
        identity = {
		    'submitter_type':'agent',
    		'submitter':'Learning Registry',
	    	'curator':'European School Net',
		    'owner':'European School Net',
		    'signer':''}
        data['identity'] = identity	 
    if data.has_key('submission_TOS'):
        changed = True
        del data['submission_TOS']
    if not data.has_key('TOS'):
        changed = True
        data['TOS'] = {
            'submission_TOS':'http://www.learningregistry.org/tos/cc0/v0-5/'
        }
		
    if data.has_key('created_timestamp'):
        changed = True
        del data['created_timestamp']
    if data.has_key('update_timestamp'):
        changed = True
        del data['update_timestamp']        
        
    if changed == True:
        data = json.dumps(data)
        with open(file_path,'w') as f:
            f.write(data)
    print file_path
