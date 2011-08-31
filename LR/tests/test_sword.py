#!/usr/bin/python
import urllib2

with open('/home/wegrata/LearningRegistryData/metadata/2011-02-28Metadata1.json','r') as f:
    data = f.read()
request = urllib2.Request('http://localhost/sword',headers={'content-type':'application/json'})
r = urllib2.urlopen(request,data)
with open('sword.htm','w') as f:
    f.write(r.read())
