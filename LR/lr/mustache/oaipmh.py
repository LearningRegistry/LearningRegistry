'''
Created on Aug 15, 2011

@author: jklo
'''
import pystache
import re
        
        
class ListIdentifiers(object):
    verb = "ListIdentifiers"
    template_prefix="""<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/OAI/2.0/OAI-PMH-LR.xsd">
  <responseDate>{{response_date}}</responseDate>
  <request verb="{{verb}}" {{#identifier}}identifier="{{identifier}}"{{/identifier}}{{#from_date}}
            from="{{from_date}}"{{/from_date}}{{#until_date}} until="{{until_date}}"{{/until_date}}{{#metadataPrefix}} 
            metadataPrefix="{{metadataPrefix}}"{{/metadataPrefix}}{{#by_doc_ID}}
            by_doc_ID="{{by_doc_ID}}"{{/by_doc_ID}}{{#by_resource_ID}} by_resource_ID="{{by_resource_ID}}"{{/by_resource_ID}}>{{path_url}}</request>
  <{{verb}}>"""
  
    template_doc = """<header><identifier>{{doc_ID}}</identifier><datestamp>{{node_timestamp}}</datestamp></header>"""

    template_suffix = """</{{verb}}></OAI-PMH>"""
    
    template_rtoken = """<resumptionToken>{{token}}</resumptionToken>"""
    
    def prefix(self, response_date, metadataPrefix, path_url, from_date=None, until_date=None):

        opts = { "response_date": response_date,
                 "from_date": from_date,
                 "until_date": until_date,
                 "metadataPrefix": metadataPrefix,
                 "path_url": path_url,
                 "verb": self.verb }
        return pystache.render(self.template_prefix, opts)
        
    def doc(self, doc=None ):
        return pystache.render(self.template_doc, doc)

    def resumptionToken(self, token=None):
        return pystache.render(self.template_rtoken, { "token": token })

    def suffix(self ):
        return pystache.render(self.template_suffix, {"verb": self.verb})
        
        
class ListRecords(ListIdentifiers):
    verb = "ListRecords"
    
    def doc(self, doc=None):
        template = '''
  <record>
    <header {{^active}}status="deleted"{{/active}}>
      <identifier>{{doc_ID}}</identifier> 
      <datestamp>{{node_timestamp}}</datestamp>
    </header>
    {{#active}}<metadata>{{{resource_data}}}</metadata>{{/active}}
  </record>'''
        doc["node_timestamp"] = re.sub("\.[0-9]+Z", "Z", doc["node_timestamp"], count=1)
        return pystache.render(template, doc)
        

class GetRecord(ListRecords):
    verb = "GetRecord"
    def prefix(self, response_date, identifier, metadataPrefix, path_url, by_doc_ID=None, by_resource_ID=None):
        opts = {"response_date": response_date,
                "identifier": identifier,
                "metadataPrefix": metadataPrefix,
                "by_doc_ID": by_doc_ID,
                "by_resource_ID": by_resource_ID,
                "path_url": path_url,
                "verb": self.verb }
        return pystache.render(self.template_prefix, opts) 

class Error(object):
    def xml(self, err=None):
        template = '''<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/OAI/2.0/OAI-PMH-LR.xsd" >
  <responseDate>{{response_date}}</responseDate>
  <request{{#verb}} verb="{{verb}}"{{/verb}}>{{path_url}}</request>
  <error code="{{code}}">{{msg}}</error>
</OAI-PMH>'''
        opts = {
                "response_date": None,
                "verb": None,
                "path_url": None,
                "code": None,
                "msg": None
                }
        for key in opts.keys():
            if key in dir(err):
                opts[key] = getattr(err,key)

        return pystache.render(template, opts)
