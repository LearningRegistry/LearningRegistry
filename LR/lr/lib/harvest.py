#!/usr/bin/python
import couchdb
import logging
import helpers as h
import iso8601
from lr.model.base_model import appConfig

log = logging.getLogger(__name__)


class harvest:
  def __init__(self, server=appConfig['couchdb.url'], database=appConfig['couchdb.db.resourcedata']):
    couchServer = couchdb.Server(server)
    self.server = couchServer
    self.db = couchServer[database]
    self.db_url = '/'.join([server,database])
  def __parse_date(self,date):
        last_update_date = iso8601.parse_date(date)
        last_update = h.convertToISO8601UTC(last_update_date)
        return last_update
  def get_record(self,id):
      try:
          return self.db[id]
      except couchdb.ResourceNotFound:
          return None

  def get_records_by_resource(self,resource_locator):
    view_data = h.getView(database_url=self.db_url,view_name='_design/learningregistry-resource-location/_view/docs',method="POST",include_docs=True,keys=[resource_locator], stale=appConfig['couchdb.stale.flag'])
    for doc in view_data:
        yield doc["doc"]

  def list_records(self, from_date, until_date,resumption_token=None, limit=None):
    return self.getViewRows(True,until_date,from_date,limit,resumption_token)

  def list_metadata_formats(self):
     return [{'metadataFormat':{'metadataPrefix':'dc'}}]

  def earliestDate(self):
    view = self.db.view('_design/learningregistry-by-date/_view/docs',limit=1,stale=appConfig['couchdb.stale.flag'])
    if len(view.rows) > 0:
      return view.rows[0].key
    else:
      return None

  def list_identifiers(self, from_date, until_date,resumption_token=None,limit=None):
    return self.getViewRows(False,until_date,from_date,limit,resumption_token)

  def getViewRows(self, includeDocs, untilDate, fromDate, limit=None, resumption_token=None):
    params = {
        'stale':appConfig['couchdb.stale.flag'],
        'include_docs':includeDocs,
        'endkey':h.convertToISO8601Zformat(untilDate),
        'startkey':h.convertToISO8601Zformat(fromDate),
      }
    if resumption_token is not None:
        params['startkey'] = resumption_token['startkey']
        params['endkey'] = resumption_token['endkey']
        params['startkey_docid'] = resumption_token['startkey_docid']
        params['skip'] = 1
    if limit is not None:
        params['limit'] = limit
    return h.getView(database_url=self.db_url,view_name='_design/learningregistry-by-date/_view/docs',**params)
if __name__ == "__main__":
  h = harvest()
  data = h.get_records_by_resource('http://www.prometheanplanet.com/server.php?show=conResource.8326')
  print len(data)
