'''
Created on Aug 15, 2011

@author: jklo
'''
import pystache
import re
from xml.dom.minidom import Text



class BaseRenderer(object):
    def __init__(self):
        pass
    
    
    def _render(self, template, context):
        def xml_escape(text):
            t = Text()
            t.data = pystache.render(text, context)
            return t.toxml("utf-8")
            
        def xml_quote(text):
            t = Text()
            t.data = pystache.render(text, context)
            return '''"{0}"'''.format(t.toxml("utf-8"))
        
        context["xE"] = xml_escape
        context["xQ"] = xml_quote
        
        return pystache.render(template, context)
    
class ListIdentifiers(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)
        self.verb = "ListIdentifiers"
        self.template_prefix="""<?xml version="1.0" encoding="UTF-8"?>
    <OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"
             xmlns:oai="http://www.openarchives.org/OAI/2.0/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/documents/downloads/OAI-PMH-LR.xsd">
      <responseDate>{{response_date}}</responseDate>
      <request  verb="{{verb}}" {{#identifier}}identifier="{{identifier}}"{{/identifier}} {{#from_date}}
                from="{{from_date}}"{{/from_date}} {{#until_date}}until="{{until_date}}"{{/until_date}} {{#metadataPrefix}} 
                metadataPrefix={{#xQ}}{{{metadataPrefix}}}{{/xQ}}{{/metadataPrefix}} {{#by_doc_ID}}
                by_doc_ID="{{by_doc_ID}}"{{/by_doc_ID}} {{#by_resource_ID}}by_resource_ID="{{by_resource_ID}}"{{/by_resource_ID}}>{{path_url}}</request>
      <{{verb}}>"""
      
        self.template_doc = """<oai:header><oai:identifier>{{doc_ID}}</oai:identifier><oai:datestamp>{{node_timestamp}}</oai:datestamp></oai:header>"""
    
        self.template_suffix = """</{{verb}}></OAI-PMH>"""
        
        self.template_rtoken = """{{#token}}<oai:resumptionToken>{{token}}</oai:resumptionToken>{{/token}}{{^token}}<oai:resumptionToken />{{/token}}"""
    

    def prefix(self, response_date, metadataPrefix, path_url, from_date=None, until_date=None):

        opts = { "response_date": response_date,
                 "from_date": from_date,
                 "until_date": until_date,
                 "metadataPrefix": metadataPrefix,
                 "path_url": path_url,
                 "verb": self.verb }
        return self._render(self.template_prefix, opts)
        
    def doc(self, doc=None ):
        return self._render(self.template_doc, doc)

    def resumptionToken(self, token=None):
        return self._render(self.template_rtoken, { "token": token })

    def suffix(self ):
        return self._render(self.template_suffix, {"verb": self.verb})
        
        
class ListRecords(ListIdentifiers):
    def __init__(self):
        ListIdentifiers.__init__(self)
        self.verb = "ListRecords"
    
    def doc(self, doc=None):
        template = '''{{#resource_data}}
  <oai:record>
    <oai:header {{^active}}status="deleted"{{/active}}>
      <oai:identifier>{{doc_ID}}</oai:identifier> 
      <oai:datestamp>{{node_timestamp}}</oai:datestamp>
    </oai:header>
    {{#active}}<oai:metadata>{{{resource_data}}}</oai:metadata>{{/active}}
  </oai:record>{{/resource_data}}'''
        doc["node_timestamp"] = re.sub("\.[0-9]+Z", "Z", doc["node_timestamp"], count=1)
        return self._render(template, doc)
        

class GetRecord(ListRecords):
    def __init__(self):
        ListRecords.__init__(self)  
        self.verb = "GetRecord"

        
    def prefix(self, response_date, identifier, metadataPrefix, path_url, by_doc_ID=None, by_resource_ID=None):
        opts = {"response_date": response_date,
                "identifier": identifier,
                "metadataPrefix": metadataPrefix,
                "by_doc_ID": by_doc_ID,
                "by_resource_ID": by_resource_ID,
                "path_url": path_url,
                "verb": self.verb }
        return self._render(self.template_prefix, opts)
    
    def doc(self, doc=None):
        template = '''{{#resource_data}}
  <record>
    <oai:header {{^active}}status="deleted"{{/active}}>
      <oai:identifier>{{doc_ID}}</oai:identifier> 
      <oai:datestamp>{{node_timestamp}}</oai:datestamp>
    </oai:header>
    {{#active}}<oai:metadata>{{{resource_data}}}</oai:metadata>{{/active}}
  </record>{{/resource_data}}'''
        doc["node_timestamp"] = re.sub("\.[0-9]+Z", "Z", doc["node_timestamp"], count=1)
        return self._render(template, doc)

class Error(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)
    
    def xml(self, err=None):
        template = '''<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"
         xmlns:oai="http://www.openarchives.org/OAI/2.0/"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/documents/downloads/OAI-PMH-LR.xsd" >
  <responseDate>{{response_date}}</responseDate>
  <request {{#verb}}verb="{{verb}}"{{/verb}}>{{path_url}}</request>
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

        return self._render(template, opts)
    
class ErrorOnly(BaseRenderer):
    def __init__(self):
        BaseRenderer.__init__(self)
    
    def xml(self, err=None):
        template = '''<error code="{{code}}">{{msg}}</error>'''
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

        return self._render(template, opts)
