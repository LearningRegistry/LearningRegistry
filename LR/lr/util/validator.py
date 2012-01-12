   # Copyright 2011 SRI International

   # Licensed under the Apache License, Version 2.0 (the "License");
   # you may not use this file except in compliance with the License.
   # You may obtain a copy of the License at

   #     http://www.apache.org/licenses/LICENSE-2.0

   # Unless required by applicable law or agreed to in writing, software
   # distributed under the License is distributed on an "AS IS" BASIS,
   # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   # See the License for the specific language governing permissions and
   # limitations under the License.

from lxml import etree
from pylons import config
import logging, os, re, subprocess

_log = logging.getLogger(__name__)

namespaces = {
              "oai" : "http://www.openarchives.org/OAI/2.0/",
              "lr" : "http://www.learningregistry.org/OAI/2.0/",
              "oai_dc" : "http://www.openarchives.org/OAI/2.0/oai_dc/",
              "oai_lr" : "http://www.learningregistry.org/OAI/2.0/oai_dc/",
              "dc":"http://purl.org/dc/elements/1.1/",
              "dct":"http://purl.org/dc/terms/",
              "nsdl_dc":"http://ns.nsdl.org/nsdl_dc_v1.02/",
              "ieee":"http://www.ieee.org/xsd/LOMv1p0",
              "xsi":"http://www.w3.org/2001/XMLSchema-instance"
              }


class XercesValidator():
    def __init__(self):
        def is_exe(fpath):
            return os.path.exists(fpath) and os.access(fpath, os.X_OK)
        
        if "xerces-c.StdInParse" in config and is_exe(config["xerces-c.StdInParse"]):
            self.stdinparse = [config["xerces-c.StdInParse"], '-n', '-f', '-s']
            self.enabled = True
        else:
            self.enabled = False
            
    def validate(self, contents=""):
        errors = []
        if self.enabled:
            process = subprocess.Popen(self.stdinparse, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            xmlin = contents 
            (_, stderr) = process.communicate(input=xmlin.encode("utf8"))
            if stderr != None or stderr != "":
                err_lines = stderr.splitlines()
                for err in err_lines:
                    m = re.match('''.*\s+line\s+([0-9]+),\s+char\s+([0-9]+)\):\s*(.*)$''', err)
                    if m is not None:
                        errors.append({ "line": m.group(1), 'char': m.group(2), 'msg': m.group(3) })
        else:
            _log.info("Xerces not available for validation.")
        return errors 

_validator = XercesValidator()


def validate_xml_content_type(res):
    content_type = None
    
    try:
        content_type = res.headers['Content-Type']
    except:
        try:
            content_type = res.headers['content-type']
        except:
            pass
        
    assert re.match("""text/xml;\s*charset=utf-8""", content_type) != None , '''Expected Content Type: "text/xml; charset=utf-8"  Got: "%s"''' % content_type
    
def validate_json_content_type(res):
    content_type = None
    
    try:
        content_type = res.headers['Content-Type']
    except:
        try:
            content_type = res.headers['content-type']
        except:
            pass
        
    assert re.match("""application/json;\s*charset=utf-8""", content_type) != None , '''Expected Content Type: "application/json; charset=utf-8"  Got: "%s"''' % content_type

def parse_response(response):
    body = response.body
    xmlcontent = etree.fromstring(body)
    
    return { "raw": body, "etree": xmlcontent }

def validate_lr_oai_etree(xmlcontent, errorExists=False, checkSchema=False, errorCodeExpected=None):
    
    error = xmlcontent.xpath("//*[local-name()='error']", namespaces=namespaces)
    if errorExists == False:
        if len(error) > 0:
            assert 0 == len(error), "validate_lr_oai_etree FAIL: Error code:{0} mesg:{1}".format(error[0].xpath("@code", namespaces=namespaces)[0], error[0].xpath("text()", namespaces=namespaces)[0])
    elif errorExists and errorCodeExpected != None:
        codeReceived = error[0].xpath("@code", namespaces=namespaces)[0]
        if errorCodeExpected != codeReceived:
            assert 0 == len(error), "validate_lr_oai_etree FAIL: Expected:{2}, Got Error code:{0} mesg:{1}".format(error[0].xpath("@code", namespaces=namespaces)[0], error[0].xpath("text()", namespaces=namespaces)[0], errorCodeExpected)
    else:
        assert 1 == len(error), "validate_lr_oai_etree FAIL: Expected error, none found."
    
    
def validate_lr_oai_response( response, errorExists=False, checkSchema=False, errorCodeExpected=None):
    validate_xml_content_type(response)
    
    obj = parse_response(response)
    xmlcontent = obj["etree"]
    validate_lr_oai_etree(xmlcontent, errorExists, checkSchema, errorCodeExpected)

    schemaErrors = _validator.validate(obj["raw"])
    assert len(schemaErrors) == 0, "validate_lr_oai_response: Schema validation error:\n%s" % '\n'.join(map(lambda x: "\t(line: {0}, char: {1}): {2}".format(x["line"], x["char"], x["msg"]), schemaErrors))
        
        