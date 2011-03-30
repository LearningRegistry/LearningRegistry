import os, zipfile
base_path = 'C:\\Documents and Settings\\admin\\Desktop\\json'
base_metadat_path ='C:\\Documents and Settings\\admin\\Desktop\\json\\20110228_eun_MDlre4_LR_0_10_0_180000'
group_sizes = [100,1000,10000,50000,100000,180000]

for group in group_sizes:
  with zipfile.ZipFile(os.path.join(base_path,'20110228_eun_MDlre4_LR_0_10_0_'+str(group)+'.zip'), 'w') as myzip:
    for i in range(0,group):   
      current_file = os.path.join(base_metadat_path,'2011-02-28Metadata'+str(i)+'.json')
      if os.path.exists(current_file):
        myzip.write(current_file,'2011-02-28Metadata'+str(i)+'.json')
  