import os, json
import ConfigParser

base_path = 'C:\\Documents and Settings\\admin\\Desktop\\json\\20110228_eun_MDlre4_LR_0_10_0_180000'

_config = ConfigParser.ConfigParser()
_config.read('testconfig.ini')
base_path = _config.get("fix", "root_path")

for file in os.listdir(base_path):
    changed = False
    file_path = os.path.join(base_path, file)
    with open(file_path,'r+') as f:
        data = json.load(f)
    
    if data.has_key('filtering_keys'):
        saved_data = data['filtering_keys']
        del data['filtering_keys']
        data['keys'] = saved_data
        changed = True

    if data.has_key('payload_schema'):
        saved_data = data['payload_schema']
        del data['payload_schema']
        data['payload_schema'] = []
        for item in saved_data:    
            data['payload_schema'][len(data['payload_schema']):] = item.split(',')
        changed = True
        
    if changed == True:
        data = json.dumps(data)
        with open(file_path,'w') as f:
            f.write(data)
    print file_path