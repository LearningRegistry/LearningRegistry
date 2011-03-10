import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.controllers.harvest import HarvestController

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class OaiPmhsController(HarvestController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('OAI-PMH', 'OAI-PMHS')

    def index(self, format='html'):
        """GET /OAI-PMHS: All items in the collection"""
        # url('OAI-PMHS')

    def create(self):
        """POST /OAI-PMHS: Create a new item"""
        # url('OAI-PMHS')

    def new(self, format='html'):
        """GET /OAI-PMHS/new: Form to create a new item"""
        # url('new_OAI-PMH')

    def update(self, id):
        """PUT /OAI-PMHS/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('OAI-PMH', id=ID),
        #           method='put')
        # url('OAI-PMH', id=ID)

    def delete(self, id):
        """DELETE /OAI-PMHS/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('OAI-PMH', id=ID),
        #           method='delete')
        # url('OAI-PMH', id=ID)

    def show(self, id, format='html'):
        """GET /OAI-PMHS/id: Show a specific item"""
        # url('OAI-PMH', id=ID)

    def edit(self, id, format='html'):
        """GET /OAI-PMHS/id/edit: Form to edit an existing item"""
        # url('edit_OAI-PMH', id=ID)
