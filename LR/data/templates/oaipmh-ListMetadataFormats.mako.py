# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1300401337.217998
_template_filename='/Users/jklo/Git/LearningRegistry-STEM-fork/LR/lr/templates/oaipmh-ListMetadataFormats.mako'
_template_uri='/oaipmh-ListMetadataFormats.mako'
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
        __M_writer(u'<?xml version="1.0" encoding="UTF-8"?>\n<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" \n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/\n         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n  <responseDate>')
        # SOURCE LINE 7
        __M_writer(filters.xml_escape(escape(c.datetime_now )))
        __M_writer(u'</responseDate>\n')
        # SOURCE LINE 8
        if c.identifier == None:
            # SOURCE LINE 9
            __M_writer(u'  <request verb="ListMetadataFormats">')
            __M_writer(filters.xml_escape(escape(c.path_url )))
            __M_writer(u'</request>\n')
            # SOURCE LINE 10
        else:   
            # SOURCE LINE 11
            __M_writer(u'    <request verb="ListMetadataFormats" identifier="')
            __M_writer(filters.xml_escape(escape(c.identifier )))
            __M_writer(u'"\n        by_doc_ID="')
            # SOURCE LINE 12
            __M_writer(filters.xml_escape(escape(c.by_doc_ID )))
            __M_writer(u'" by_resource_ID="')
            __M_writer(filters.xml_escape(escape(c.by_resource_ID )))
            __M_writer(u'">')
            __M_writer(filters.xml_escape(escape(c.path_url )))
            __M_writer(u'</request>\n')
            pass
        # SOURCE LINE 14
        __M_writer(u'  <ListMetadataFormats>\n')
        # SOURCE LINE 15
        for fmt in c.formats:
            # SOURCE LINE 16
            __M_writer(u'   <metadataFormat>\n    <metadataPrefix>')
            # SOURCE LINE 17
            __M_writer(filters.xml_escape(escape(fmt["metadataPrefix"] )))
            __M_writer(u'</metadataPrefix>\n    <schema>')
            # SOURCE LINE 18
            __M_writer(filters.xml_escape(escape(fmt["schemas"][0] )))
            __M_writer(u'</schema>\n   </metadataFormat>\n')
            pass
        # SOURCE LINE 21
        __M_writer(u'  </ListMetadataFormats>\n</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


