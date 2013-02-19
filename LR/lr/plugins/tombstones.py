# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

from lr.plugins.base import BasePlugin

class DoNotPublishError(Exception):
  pass

class ITombstonePolicy(BasePlugin):
    
    def __init__(self):
        super(ITombstonePolicy, self).__init__()

    def permit(self, original_rd3=None, original_crypto=None, replacement_rd3=None, replacement_crypto=None):
        '''Is executed on the original resource data with the replacement document.
           This function should return True if implemented policy should allow a
           tombstone to be created for the original document.'''

        raise NotImplementedError("permit function must be implemented.")

    def permit_burial(self, replacement_rd3=None, replacement_crypto=None, graveyard=[], existing_gravestones=[]):
        '''This is executed to validate that for the specified replacement_rd3, all tombstones in
           the graveyard are allowed to be buried. Use this to implement a specific node policy.
           Return True to permit tombstone persistence and replacement_rd3 persistence, False otherwise.'''

        raise NotImplementedError("permit_burial function must be implemented")

ITombstonePolicy.ID = "Tombstone Policy"