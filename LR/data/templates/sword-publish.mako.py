# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1301083146.4537079
_template_filename='/home/wegrata/LearningRegistry/LR/lr/templates/sword-publish.mako'
_template_uri='sword-publish.mako'
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
        # SOURCE LINE 1
        __M_writer(u'<?xml version="1.0"?>\n\n   <entry xmlns="http://www.w3.org/2005/Atom"\n\t xmlns:sword="http://purl.org/net/sword/">\n     <title>')
        # SOURCE LINE 5
        __M_writer(filters.xml_escape(escape(c.doc["doc_ID"] )))
        __M_writer(u'</title>\n     <id>')
        # SOURCE LINE 6
        __M_writer(filters.xml_escape(escape(c.doc["doc_ID"] )))
        __M_writer(u'</id>\n')
        # SOURCE LINE 7
        if c.no_op:
            # SOURCE LINE 8
            __M_writer(u'         <sword:noOp>true</sword:noOp>\n')
            pass
        # SOURCE LINE 10
        if c.verbose:
            # SOURCE LINE 11
            __M_writer(u'         <sword:verboseDescription>\n            Does collection exist? True.\n            User authenticates? True.\n            User: ')
            # SOURCE LINE 14
            __M_writer(escape(c.on_behalf_of))
            __M_writer(u'\n            User has rights to collection? True. \n         </sword:verboseDescription>\n')
            pass
        # SOURCE LINE 18
        __M_writer(u'     <updated>')
        __M_writer(escape(c.doc['update_timestamp']))
        __M_writer(u'</updated>\n\n     <author><name>Learning Registry</name></author>\n     <summary type="text">A summary</summary>\n     <sword:userAgent>')
        # SOURCE LINE 22
        __M_writer(escape(c.user_agent))
        __M_writer(u'</sword:userAgent>\n     <generator uri="')
        # SOURCE LINE 23
        __M_writer(escape(c.generator_url))
        __M_writer(u'" version="1.0"/>\n     <content type="application/json" src="')
        # SOURCE LINE 24
        __M_writer(escape(c.content_url))
        __M_writer(u'"/>\t\n  </entry>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


