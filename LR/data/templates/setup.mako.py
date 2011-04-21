# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1302627626.3156381
_template_filename='/home/wegrata/LearningRegistry/LR/lr/templates/setup.mako'
_template_uri='setup.mako'
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
        __M_writer(u'<html>\n    <head>\n        <title>LR Setup</title>\n        <style type="text/css">\n            div span {\n                display: inline-block;\n                width: 150px;\n                text-align:right;\n            }\n        </style>\n    </head>\n    <body>\n        <form name="setup" method="POST" action="/setup">\n             <div><span>Node Name:</span><input type=\'text\' name=\'nodeName\'/></div>\n             <div><span>Node ID:</span><input type=\'text\' name=\'nodeID\'/></div>\n             <div><span>Network Name:</span><input type=\'text\' name=\'networkName\'/></div>\n             <div><span>Network ID:</span><input type=\'text\' name=\'networkID\'/></div>\n             <div><span>Community Name:</span><input type=\'text\' name=\'communityName\'/></div>\n             <div><span>Community ID:</span><input type=\'text\' name=\'communityID\'/></div>\n             <div>                          \n                <input type="submit" name="submit" value="Submit" />\n             </div>\n        </form>\n    </body>\n</html>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


