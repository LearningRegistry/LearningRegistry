#!/usr/bin/python
import couchdb
import logging
import helpers as h
import iso8601
from lr.model.base_model import appConfig

log = logging.getLogger(__name__)
class harvest:
  def __init__(self, server=appConfig['couchdb.url'], database='resource_data'):
    server = couchdb.Server(server)
    self.db = server[database]
  def __parse_date(self,date):
        last_update_date = iso8601.parse_date(date)
        last_update = h.convertToISO8601UTC(last_update_date)    
        return last_update
  def get_record(self,id):
    return self.db[id]
  def get_records_by_resource(self,resource_locator):
    view_data = self.db.view('_design/learningregistry/_view/resource-location',include_docs=True,keys=[resource_locator])
    return map(lambda doc: doc.doc, view_data)      
  def list_records(self, from_date, until_date):
    
    rows = self.db.view('_design/learningregistry/_view/by-date',startkey=h.convertToISO8601Zformat(from_date),endkey=h.convertToISO8601Zformat(until_date), include_docs=True)
    for row in rows:
      #ignore design docs
      if not row.id.startswith('_design'):
          yield row.doc
  def list_metadata_formats(self):
     return [{'metadataFormat':{'metadataPrefix':'dc'}}]

  def list_identifiers(self, from_date, until_date):
    rows = self.db.view('_design/learningregistry/_view/by-date',startkey=h.convertToISO8601Zformat(from_date),endkey=h.convertToISO8601Zformat(until_date))
    return_list = []
    for row in rows:
      #ignore design docs
      if not row.id.startswith('_design'):
          yield (row.id)

if __name__ == "__main__":
  h = harvest()
  data = h.get_records_by_resource('http://www.prometheanplanet.com/server.php?show=conResource.8326')
  print len(data)
