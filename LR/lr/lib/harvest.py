#!/usr/bin/python
import couchdb, json
from datetime import datetime

class harvest:
  def __init__(self, server='http://localhost:5984', database='resource_data'):
    server = couchdb.Server(server)
    self.db = server[database]

  def get_record(self,id):
    return self.db[id]
  def get_records_by_resource(self,resource_locator):
    view_data = self.db.view('_design/learningregistry/_view/resource-location',include_docs=True,keys=[resource_locator])
    return map(lambda doc: doc.doc, view_data)      
  def list_records(self, from_date, until_date):
    rows = self.db.view('_all_docs', include_docs=True)
    return_list = []
    for row in rows:
      #ignore design docs
      if not row.id.startswith('_design'):
        last_update = datetime.strptime(row.doc['update_timestamp'],'%Y-%m-%d %H:%M:%S.%f')
        if last_update >=from_date or last_update <= until_date:
          return_list.append(row.doc)
    return return_list
  def list_metadata_formats(self):
     return [{'metadataPrefix':'dc'}]

  def list_identifiers(self, from_date, until_date):
    rows = self.db.view('_all_docs', include_docs=True)
    return_list = []
    for row in rows:
      #ignore design docs
      if not row.id.startswith('_design'):
        last_update = datetime.strptime(row.doc['update_timestamp'],'%Y-%m-%d %H:%M:%S.%f')
        if last_update >=from_date or last_update <= until_date:
          return_list.append(row.id)
    return return_list

if __name__ == "__main__":
  h = harvest()
  data = h.get_records_by_resource('http://www.prometheanplanet.com/server.php?show=conResource.8326')
  print len(data)
