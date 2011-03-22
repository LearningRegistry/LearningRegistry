# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1300344785.477747
_template_filename='/Users/jklo/Git/LearningRegistry-STEM-fork/LR/lr/templates/oaipmh-Identify.mako'
_template_uri='/oaipmh-Identify.mako'
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
        __M_writer(u'\n<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/" \n         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n         xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/\n         http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">\n  <responseDate>')
        # SOURCE LINE 11
        __M_writer(filters.xml_escape(escape(c.datetime_now )))
        __M_writer(u'</responseDate>\n  <request verb="Identify">')
        # SOURCE LINE 12
        __M_writer(filters.xml_escape(escape(c.path_url )))
        __M_writer(u'</request>\n  <Identify>\n    <repositoryName>')
        # SOURCE LINE 14
        __M_writer(filters.xml_escape(escape(c.identify["repositoryName"] )))
        __M_writer(u'</repositoryName>\n    <baseURL>')
        # SOURCE LINE 15
        __M_writer(filters.xml_escape(escape(c.path_url )))
        __M_writer(u'</baseURL>\n    <protocolVersion>2.0</protocolVersion>\n    <adminEmail>')
        # SOURCE LINE 17
        __M_writer(filters.xml_escape(escape(c.identify["adminEmail"] )))
        __M_writer(u'</adminEmail>\n    <earliestDatestamp>')
        # SOURCE LINE 18
        __M_writer(filters.xml_escape(escape(h.convertToISO8601Zformat(c.identify["earliestDatestamp"]) )))
        __M_writer(u'</earliestDatestamp>\n    <deletedRecord>')
        # SOURCE LINE 19
        __M_writer(filters.xml_escape(escape(c.identify["deletedRecord"] )))
        __M_writer(u'</deletedRecord>\n    <granularity>')
        # SOURCE LINE 20
        __M_writer(filters.xml_escape(escape(c.identify["granularity"] )))
        __M_writer(u'</granularity>\n </Identify>\n</OAI-PMH>')
        return ''
    finally:
        context.caller_stack._pop_frame()


