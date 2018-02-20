#!/usr/bin/python
import os, json, errno, codecs
import ConfigParser
import types
import re
_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
base_path = _config.get("fix", "root_path")
out_path = _config.get("fix", "out_path")

if out_path == None:
    out_path = base_path

def goodPayloadSchema(ps):
    isGood = True
    if ps is not None and isinstance(ps, types.ListType):
         for s in ps:
             isGood &= len(s) > 1
    return isGood

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

for fname in os.listdir(base_path):
    changed = False
    file_path = os.path.join(base_path, fname)
    if os.path.isdir(file_path) or re.match("^\\.", fname, flags=re.IGNORECASE) is not None:
        continue
    with codecs.open(file_path,'r+', 'utf-8-sig') as f:
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
		    'owner':'European School Net'
#		    'signer':''
        }
        data['identity'] = identity
    if data.has_key('submission_TOS'):
        changed = True
        del data['submission_TOS']
    if not data.has_key('TOS'):
        changed = True
        data['TOS'] = {
            'submission_TOS':'https://www.learningregistry.org/tos/cc0/v0-5/'
        }

    if data.has_key('payload_schema') and not goodPayloadSchema(data['payload_schema']):
        bad = data['payload_schema']
        better = "".join(bad)
        good = re.split("\\s+", better)
        data['payload_schema'] = good
        changed = True


    if data.has_key('created_timestamp'):
        changed = True
        del data['created_timestamp']
    if data.has_key('update_timestamp'):
        changed = True
        del data['update_timestamp']

    if data.has_key('publishing_node'):
        del data['publishing_node']

    if changed == True:
        data = json.dumps(data, sort_keys=True, indent=4)
        mkdir_p(out_path)
        out_file = os.path.join(out_path, fname)
#        with open(out_file,'w' ) as f:
#            f.write(data)
        with codecs.open(out_file,'w', "utf-8-sig" ) as f:
#            f.write(u'\ufeff')
            f.write(data)
            f.close()
    print out_file
