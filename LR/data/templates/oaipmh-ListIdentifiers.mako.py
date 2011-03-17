# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1300240261.118155
_template_filename='/Users/jklo/Git/LearningRegistry-STEM-fork/LR/lr/templates/oaipmh-ListIdentifiers.mako'
_template_uri='/oaipmh-ListIdentifiers.mako'
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
        len = context.get('len', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<?xml version="1.0" encoding="UTF-8"?>\n')
        # SOURCE LINE 6
        __M_writer(u'\n<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" \n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/\n         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n  <responseDate>')
        # SOURCE LINE 11
        __M_writer(filters.xml_escape(escape(c.datetime_now )))
        __M_writer(u'</responseDate>\n  <request verb="ListIdentifiers" \n            from="')
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
        __M_writer(u'</request>\n  <ListIdentifiers>\n')
        # SOURCE LINE 17
        if c.identifiers != None and len(c.identifiers) > 0:
            # SOURCE LINE 18
            for ident in c.identifiers:
                # SOURCE LINE 19
                __M_writer(u'       <header>  \n        <identifier>')
                # SOURCE LINE 20
                __M_writer(filters.xml_escape(escape(ident["doc_ID"] )))
                __M_writer(u'</identifier>\n        ')
                # SOURCE LINE 21
                tstamp = iso8601.parse_date(ident["node_timestamp"]) 
                
                __M_locals_builtin_stored = __M_locals_builtin()
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['tstamp'] if __M_key in __M_locals_builtin_stored]))
                __M_writer(u'<datestamp>')
                __M_writer(filters.xml_escape(escape(h.convertToISO8601Zformat(tstamp) )))
                __M_writer(u'</datestamp>\n       </header>\n')
                pass
            pass
        # SOURCE LINE 25
        __M_writer(u' </ListIdentifiers>\n</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


