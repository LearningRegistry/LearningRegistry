# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1299866174.462942
_template_filename='/Users/jklo/Git/LearningRegistry-STEM-fork/LR/lr/templates/oaipmh-GetRecord.mako'
_template_uri='/oaipmh-GetRecord.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<?xml version="1.0" encoding="UTF-8"?> \n<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" \n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/\n         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n  <responseDate>')
        # SOURCE LINE 7
        __M_writer(filters.xml_escape(escape(c.datetime_now )))
        __M_writer(u'</responseDate>\n  <request verb="GetRecord" identifier="')
        # SOURCE LINE 8
        __M_writer(filters.xml_escape(escape(c.doc["doc_ID"] )))
        __M_writer(u'"\n           metadataPrefix="')
        # SOURCE LINE 9
        __M_writer(filters.xml_escape(escape(c.metadataPrefix )))
        __M_writer(u'">')
        __M_writer(filters.xml_escape(escape(c.path_url )))
        __M_writer(u'</request>\n  <GetRecord>\n   <record> \n    <header>\n      <identifier>')
        # SOURCE LINE 13
        __M_writer(filters.xml_escape(escape(c.doc["doc_ID"] )))
        __M_writer(u'</identifier> \n      <datestamp>')
        # SOURCE LINE 14
        __M_writer(filters.xml_escape(escape(c.doc["create_timestamp"] )))
        __M_writer(u'</datestamp>\n    </header>\n    <metadata>\n      ')
        # SOURCE LINE 17
        __M_writer(c.doc["resource_data"] )
        __M_writer(u'\n    </metadata>\n  </record>\n </GetRecord>\n</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


