#!/usr/bin/python
request = {
    'body': 'undefined',
    'cookie': {
        '__utma': '96992031.3087658685658095000.1224404084.1226129950.1226169567.5',
        '__utmz': '96992031.1224404084.1.1.utmcsr'
    },
    'form': {},
    'info': {
        'compact_running': False,
        'db_name': 'couchbox',
        'disk_size': 50559251,
        'doc_count': 9706,
        'doc_del_count': 0,
        'purge_seq': 0,
        'update_seq': 9706},
    'path': [],
    'query': {},
    'method': 'GET'
}
import json, urllib2
data = json.dumps(request)
print data
response = urllib2.urlopen('http://127.0.0.1:5984/_test',data)
print response.read()
