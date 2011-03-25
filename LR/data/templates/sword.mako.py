# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1301076671.6363821
_template_filename='/home/wegrata/LearningRegistry/LR/lr/templates/sword.mako'
_template_uri='sword.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
from webhelpers.html import escape
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<?xml version="1.0" encoding=\'utf-8\'?>\n<service xmlns="http://www.w3.org/2007/app"\n         xmlns:atom="http://www.w3.org/2005/Atom"\n\t xmlns:sword="http://purl.org/net/sword/"\n\t xmlns:dcterms="http://purl.org/dc/terms/">\n\n <sword:version>1.3</sword:version>\n <workspace>\n   <atom:title>Learning Registry</atom:title>\n   <collection\n       href="{$c.content_url}" >\n     <atom:title>Learning Registry</atom:title>\n     <accept>application/json</accept>\n     <sword:collectionPolicy>Collection Policy</sword:collectionPolicy>\n     <dcterms:abstract>Learning Registry</dcterms:abstract>\n   </collection>\n </workspace>\n</service>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


