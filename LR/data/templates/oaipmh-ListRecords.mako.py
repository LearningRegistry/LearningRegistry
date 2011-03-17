# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1300240589.179305
_template_filename='/Users/jklo/Git/LearningRegistry-STEM-fork/LR/lr/templates/oaipmh-ListRecords.mako'
_template_uri='/oaipmh-ListRecords.mako'
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
        __M_writer(u'<?xml version="1.0" encoding="UTF-8"?>\n')
        # SOURCE LINE 6
        __M_writer(u'\n<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" \n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/\n         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n <responseDate>')
        # SOURCE LINE 11
        __M_writer(filters.xml_escape(escape(c.datetime_now )))
        __M_writer(u'</responseDate> \n <request verb="ListRecords"\n            from="')
        # SOURCE LINE 13
        __M_writer(filters.xml_escape(escape(c.from_date )))
        __M_writer(u'"\n            until="')
        # SOURCE LINE 14
        __M_writer(filters.xml_escape(escape(c.until_date )))
        __M_writer(u'" \n            metadataPrefix="')
        # SOURCE LINE 15
        __M_writer(filters.xml_escape(escape(c.metadataPrefix )))
        __M_writer(u'">')
        __M_writer(filters.xml_escape(escape(c.path_url )))
        __M_writer(u'</request>\n <ListRecords>\n')
        # SOURCE LINE 17
        for doc in c.records:
            # SOURCE LINE 18
            if doc["active"] == True:
                # SOURCE LINE 19
                __M_writer(u'  <record>\n    <header>\n      <identifier>')
                # SOURCE LINE 21
                __M_writer(filters.xml_escape(escape(doc["doc_ID"] )))
                __M_writer(u'</identifier> \n      ')
                # SOURCE LINE 22
                tstamp = iso8601.parse_date(doc["node_timestamp"]) 
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['tstamp'] if __M_key in __M_locals_builtin_stored]))
                __M_writer(u'<datestamp>')
                __M_writer(filters.xml_escape(escape(h.convertToISO8601Zformat(tstamp) )))
                __M_writer(u'</datestamp>\n    </header>\n    <metadata>\n        ')
                # SOURCE LINE 25
                __M_writer(doc["resource_data"] )
                __M_writer(u' \n    </metadata>\n  </record>\n')
                # SOURCE LINE 28
            else:
                # SOURCE LINE 29
                __M_writer(u'  <record>\n    <header status="deleted">\n      <identifier>')
                # SOURCE LINE 31
                __M_writer(filters.xml_escape(escape(doc["doc_ID"] )))
                __M_writer(u'</identifier>\n      ')
                # SOURCE LINE 32
                tstamp = iso8601.parse_date(doc["node_timestamp"]) 
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['tstamp'] if __M_key in __M_locals_builtin_stored]))
                __M_writer(u'<datestamp>')
                __M_writer(filters.xml_escape(escape(h.convertToISO8601Zformat(tstamp) )))
                __M_writer(u'</datestamp>\n    </header>\n  </record>\n')
                pass
            pass
        # SOURCE LINE 37
        __M_writer(u' </ListRecords>\n</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


