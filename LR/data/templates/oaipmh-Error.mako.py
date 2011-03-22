# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1300418322.830195
_template_filename='/home/wegrata/LearningRegistry/LR/lr/templates/oaipmh-Error.mako'
_template_uri='oaipmh-Error.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        c = context.get('c', UNDEFINED)
        hasattr = context.get('hasattr', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<?xml version="1.0" encoding="UTF-8"?>\n<OAI-PMH xmlns="http://www.learningregistry.org/OAI/2.0/"\n         xmlns:oai="http://www.openarchives.org/OAI/2.0/"\n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://www.learningregistry.org/OAI/2.0/ http://www.learningregistry.org/OAI/2.0/OAI-PMH-LR.xsd" >\n  <responseDate>')
        # SOURCE LINE 7
        __M_writer(filters.xml_escape(escape(c.error.datetime_now )))
        __M_writer(u'</responseDate>\n')
        # SOURCE LINE 8
        if hasattr(c.error, 'verb'):
            # SOURCE LINE 9
            __M_writer(u'  <request verb="')
            __M_writer(filters.xml_escape(escape(c.error.verb )))
            __M_writer(u'">')
            __M_writer(filters.xml_escape(escape(c.error.path_url )))
            __M_writer(u'</request>\n')
            # SOURCE LINE 10
        else:
            # SOURCE LINE 11
            __M_writer(u'  <request>')
            __M_writer(filters.xml_escape(escape(c.error.path_url )))
            __M_writer(u'</request>\n')
            pass
        # SOURCE LINE 13
        __M_writer(u'  <error code="')
        __M_writer(filters.xml_escape(escape(c.error.code )))
        __M_writer(u'">')
        __M_writer(filters.xml_escape(escape(c.error.msg )))
        __M_writer(u'</error>\n</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


