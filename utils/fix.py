import os, json

base_path = '/home/wegrata/Downloads/test_data'

for file in os.listdir(base_path):
  file_path = os.path.join(base_path, file)
  with open(file_path,'r+') as f:
    data = json.load(f)
  data['keys'] =["EUN", "LOM"]
  data = json.dumps(data)
  with open(file_path,'w') as f:
      f.write(data)
  print file_path
