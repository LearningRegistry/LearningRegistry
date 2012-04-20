from lr.tests import *
from nose.tools import raises
import logging,json
import time
from urllib import unquote_plus,quote_plus
from pylons import config
from datetime import datetime
from lr.lib.harvest import harvest
import threading
import math
import time
from  iso8601 import parse_date
from datetime import datetime
from lr.util.decorators import ForceCouchDBIndexing
from httplib import HTTPException
from couchapp import config as cfg, commands as cmd
from pylons import config
import sys

log = logging.getLogger(__name__)
headers={'content-type': 'application/json'}
db = None

def _pushCouchApp(sourceDir, destURL):
    try:
        conf = cfg.Config()
        cmd.push(conf, sourceDir, destURL)
        print("Deployed CouchApp from '{0}' to '{1}'".format(sourceDir, destURL))
    except:
        print repr(sys.exc_info())
        print("Unable to push CouchApp at '{0}'".format(sourceDir))

class TestExtractController(TestController):
    def _convertDateTime(self,dt):
        epoch = parse_date("1970-01-01T00:00:01Z")
        if isinstance(dt, str) or isinstance(dt,unicode):
            dt = parse_date(dt)
        dt = dt - epoch
        return int(math.floor(dt.total_seconds()))
    def _validateJsonStructure(self,data):        
        assert "documents" in data
        assert len(data['documents']) > 0
        for doc in data['documents']:
            assert "result_data" in doc
            assert "resource_data" in doc
    def _validateDiscriminator(self,data,discriminator):
        for doc in data['documents']:
            assert doc['result_data']['discriminator'].startswith(discriminator)
    def _validateUntil(self,data,until):
        until = self._convertDateTime(until)
        for doc in data['documents']:
            for envelope in  doc['resource_data']:
                timestamp = self._convertDateTime(envelope['node_timestamp'])
                assert timestamp <= until
    def _validateFrom(self,data,f):
        f = self._convertDateTime(f)
        for doc in data['documents']:
            for envelope in  doc['resource_data']:
                timestamp = self._convertDateTime(envelope['node_timestamp'])
                assert timestamp >= f
    
    @classmethod
    def setupClass(self):
        self.setup = True
        with open("lr/tests/data/nsdl_dc/data-000000000.json",'r') as f:
            data = json.load(f)
        if hasattr(self, "attr"):
            app = self.app
        else:
            controller =  TestExtractController(methodName="test_empty")
            app = controller.app  
        h = harvest()
        self.db = h.db                      
        self.server = h.server
        global db
        db = self.db
        result = app.post('/publish', params=json.dumps(data), headers=headers)        
        result = json.loads(result.body)
        self.ids = []
        self.ids.extend(map(lambda doc: doc['doc_ID'],result['document_results']))
        result = app.post('/publish', params=json.dumps(data), headers=headers)        
        result = json.loads(result.body)
        self.ids.extend(map(lambda doc: doc['doc_ID'],result['document_results']))
        self.resourceLocators = map(lambda doc: doc['resource_locator'],data['documents'])
        done = False
        distributableIds = map(lambda id: id+'-distributable',self.ids)
        while not done:      
            view = self.db.view('_all_docs',keys=distributableIds)                
            done = len(distributableIds) == len(view.rows)
            time.sleep(0.5)

        #install data_service view  
        couchdb_url = config['couchdb.url']
        resource_data_db = config['couchdb.db.resourcedata']

        _pushCouchApp("../data_services/standards-alignment-dct-conformsTo", "{0}/{1}".format(couchdb_url,resource_data_db))

    def test_empty(self):
        pass
    @classmethod
    def tearDownClass(self):
        for id in self.ids:
            try:
                del self.db[id]
            except:
                pass
            try:
                del self.db[id+'-distributable']
            except:
                pass
    @ForceCouchDBIndexing()
    def test_get(self):
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json'))
        data = json.loads(response.body)
        self._validateJsonStructure(data)
    @ForceCouchDBIndexing()
    def test_get_resource(self):
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-resource/format/to-json'))
        data = json.loads(response.body)
        self._validateJsonStructure(data)        
    @ForceCouchDBIndexing()
    def test_get_with_discriminator(self):
        discriminator = "http://purl.org/ASN/"
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json',discriminator=discriminator))
        data = json.loads(response.body)
        self._validateJsonStructure(data)
        self._validateDiscriminator(data,discriminator)        
    @ForceCouchDBIndexing()
    def test_get_with_from(self):
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json'),params={"from":self.from_date})
        data = json.loads(response.body)
        self._validateJsonStructure(data)
        self._validateFrom(data,self.from_date)
    @ForceCouchDBIndexing()
    def test_get_with_until(self):
        until_date = datetime.utcnow().isoformat()+"Z"
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json',until=until_date))
        data = json.loads(response.body)
        self._validateJsonStructure(data)                
        self._validateUntil(data,until_date)
    @ForceCouchDBIndexing()
    def test_get_with_discriminator_until(self):
        discriminator = "http://purl.org/ASN/"
        until_date = datetime.utcnow().isoformat()+"Z"
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json',discriminator=discriminator,until=until_date))
        data = json.loads(response.body)
        self._validateJsonStructure(data)
        self._validateDiscriminator(data,discriminator)          
        self._validateUntil(data,until_date)
    @ForceCouchDBIndexing()
    def test_get_with_discriminator_from(self):
        discriminator = "http://purl.org/ASN/"
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json'),params={"discriminator":discriminator,"from":self.from_date})
        data = json.loads(response.body)
        self._validateJsonStructure(data)
        self._validateDiscriminator(data,discriminator)                  
        self._validateFrom(data,self.from_date)
    @ForceCouchDBIndexing()
    def test_get_with_discriminator_from_until(self):
        discriminator = "http://purl.org/ASN/"
        until_date = datetime.utcnow().isoformat()+"Z"
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json'),params={"discriminator":discriminator,"from":self.from_date, "until":until_date})
        data = json.loads(response.body)
        self._validateJsonStructure(data)
        self._validateDiscriminator(data,discriminator)                          
        self._validateFrom(data,self.from_date)
        self._validateUntil(data,until_date)
    @ForceCouchDBIndexing()
    def test_get_with_from_junk_date(self):
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json'),params={"from":"abc123"},status=500)
        data = json.loads(response.body)
        assert not data['OK']
    @ForceCouchDBIndexing()
    def test_get_with_until_junk_date(self):
        response = self.app.get(url('/extract/standards-alignment-dct-conformsTo/discriminator-by-ts/format/to-json'),params={"until":"abc123"},status=500)
        data = json.loads(response.body)
        assert not data['OK']        
    def test_invalid_Data_service(self):
        response = self.app.get(url('/extract/learningregistry-slice/docs/format/to-json'),status=406)