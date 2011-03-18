import os, json

base_path = 'C:\\Documents and Settings\\admin\\Desktop\\json\\20110228_eun_MDlre4_LR_0_10_0_180000'

for file in os.listdir(base_path):
  file_path = os.path.join(base_path, file)
  with open(file_path,'r+') as f:
    data = json.load(f)
  saved_data = data['filtering_keys']
  del data['filtering_keys']
  data['keys'] = saved_data
  data = json.dumps(data)
  with open(file_path,'w') as f:
      f.write(data)
  print file_path