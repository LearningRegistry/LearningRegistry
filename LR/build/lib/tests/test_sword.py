#!/usr/bin/python
import urllib2
import codecs
with codecs.open('/home/wegrata/data/LearningRegistryData/paradata/0.21.0/paradata0000/2011-06-12Paradata000498.json','r+', 'utf-8-sig') as f:
    data = f.read()
request = urllib2.Request('http://localhost/swordpub',headers={'Content-Type':'application/json'})
r = urllib2.urlopen(request,data)
data = r.read()
print data
with open('sword.htm','w') as f:
    f.write(data)
