# !/usr/bin/python
# Copyright 2011 Lockheed Martin

'''

Created on August 31, 2011

@author: jpoyau
'''
from lr.lib.couch_change_monitor import BaseViewsUpdateHandler

_RESOURCE_DATA_TYPE = "resource_data"
_DOC_TYPE = "doc_type"
_DOC = "doc"


class UpdateViewsHandler(BaseViewsUpdateHandler):
    """Class to update the views in the resource """
    def _canHandle(self, change, database):
        if ((_DOC in change) and 
            (change[_DOC].get(_DOC_TYPE) ==_RESOURCE_DATA_TYPE)) :
                return True
        return False
