# Copyright 2012 SRI International

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this 
# file except in compliance with the License. You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under the License 
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express 
# or implied. See the License for the specific language governing permissions and limitations under 
# the License.

# This project has been funded at least or in part with Federal funds from the U.S. Department of 
# Education under Contract Number ED-04-CO-0040/0010. The content of this publication does not 
# necessarily reflect the views or policies of the U.S. Department of Education nor does mention 
# of trade names, commercial products, or organizations imply endorsement by the U.S. Government.

import logging
import os
import tempfile
from subprocess import Popen, PIPE, STDOUT

from couchapp.localdoc import document
from couchapp import util
from nose import tools

# need this decorator to tell nose that this thing isn't a test
@tools.nottest
def test(conf, path, *args, **opts):
    export = opts.get('export', False)
    js = opts.get('spidermonkey', 'js');
    test_file = args[0]
    dest = None
    doc_path = None
    # print("path: {0}".format(path))
    # print("test_file: {0}".format(args))
    # print("conf: {0}".format(conf))
    if len(args) < 2:
        if export:
            if path is None and args:
                doc_path = args[0]
            else:
                doc_path = path
        else:
            doc_path = path
            if args:
                dest = args[0]
    else:
        doc_path = os.path.normpath(os.path.join(os.getcwd(), args[0]))
        dest = args[1]
    if doc_path is None:
        raise AppError("You aren't in a couchapp.")
    
    # print ("docPath:"+doc_path)
    conf.update(doc_path)

    doc = document(doc_path, create=False, 
                        docid=opts.get('docid'))
    if export:
        if opts.get('output'):
            util.write_json(opts.get('output'), str(doc))
        else:
            print str(doc)
        return 0

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write("var couchdb_design_doc = {0};".format(str(doc)))
        tmp.flush()
        print(tmp.name)
        # util.write_json(tmp.name, str(doc))
        
        p = Popen([js, test_file, tmp.name], stdout=PIPE, stderr=PIPE)
        # status = 1
        # while status >= 0:
        stdout, stderr = p.communicate()
        print "OUT:\n"+stdout
        print "ERROR:\n"+stderr
            # status = p.poll()

    return 0

cmdtable = {
    "test": (test,
        [
            ("js", "spidermonkey", "js", "Path to Spidermonkey JS."),
            ("x", "export", '', "Write design document to file or STDOUT."),
            ("o", "output", '', "Path to export to or STDOUT")
        ],
        "Execute unit tests against design document")
}


