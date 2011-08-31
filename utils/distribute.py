#!/usr/bin/python
import couchdb, urllib2,time
target_dist_url = 'http://localhost/distribute'
couchdb_url = 'http://localhost:5984/resource_data'
change_threshold = 100
sleep_time = 60
if __name__ == '__main__':
    db = couchdb.Database(couchdb_url)
    last_seq = ''
    while True:
        time.sleep(sleep_time)        
        if last_seq <> '':
            changes = db.changes(since=last_seq)    
        else:
            changes = db.changes()
        last_seq = changes['last_seq'] 
        if len(changes['results']) >= change_threshold:
            urllib2.urlopen(target_dist_url,'test')
