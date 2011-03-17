# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1300238328.764117
_template_filename='/Users/jklo/Git/LearningRegistry-STEM-fork/LR/lr/templates/oaipmh-GetRecord.mako'
_template_uri='/oaipmh-GetRecord.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


# SOURCE LINE 3

from datetime import datetime
import iso8601


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<?xml version="1.0" encoding="UTF-8"?> \n')
        # SOURCE LINE 6
        __M_writer(u'\n<OAI-PMH \n            xmlns="http://www.learningregistry.org/OAI/2.0/"\n            xmlns:oai="http://www.openarchives.org/OAI/2.0/"\n            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n            xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/OAI/2.0/OAI-PMH-LR.xsd" \n>\n  <responseDate>')
        # SOURCE LINE 13
        __M_writer(filters.xml_escape(escape(c.datetime_now )))
        __M_writer(u'</responseDate>\n  <request verb="GetRecord" identifier="')
        # SOURCE LINE 14
        __M_writer(filters.xml_escape(escape(c.identifier )))
        __M_writer(u'"\n           metadataPrefix="')
        # SOURCE LINE 15
        __M_writer(filters.xml_escape(escape(c.metadataPrefix )))
        __M_writer(u'"\n           by_doc_ID="')
        # SOURCE LINE 16
        __M_writer(filters.xml_escape(escape(c.by_doc_ID )))
        __M_writer(u'"\n           by_resource_ID="')
        # SOURCE LINE 17
        __M_writer(filters.xml_escape(escape(c.by_resource_ID )))
        __M_writer(u'">')
        __M_writer(filters.xml_escape(escape(c.path_url )))
        __M_writer(u'</request>\n')
        # SOURCE LINE 18
        if c.docList != None:
            # SOURCE LINE 19
            __M_writer(u'  <GetRecord>\n')
            # SOURCE LINE 20
            for doc in c.docList:
                # SOURCE LINE 21
                __M_writer(u'   <record> \n    <oai:header>\n      <oai:identifier>')
                # SOURCE LINE 23
                __M_writer(filters.xml_escape(escape(doc["doc_ID"] )))
                __M_writer(u'</oai:identifier> \n      ')
                # SOURCE LINE 24

                tstamp = iso8601.parse_date(doc["node_timestamp"])
                      
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['tstamp'] if __M_key in __M_locals_builtin_stored]))
                # SOURCE LINE 26
                __M_writer(u'\n      <oai:datestamp>')
                # SOURCE LINE 27
                __M_writer(filters.xml_escape(escape(h.convertToISO8601Zformat(tstamp) )))
                __M_writer(u'</oai:datestamp>\n    </oai:header>\n    <oai:metadata>\n      ')
                # SOURCE LINE 30
                __M_writer(doc["resource_data"] )
                __M_writer(u'\n    </oai:metadata>\n  </record>\n')
                pass
            # SOURCE LINE 34
            __M_writer(u' </GetRecord>\n')
            pass
        # SOURCE LINE 36
        __M_writer(u'</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


