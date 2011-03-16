import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SwordController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('sword', 'sword')

    def index(self, format='html'):
        """GET /sword: All items in the collection"""
        # url('sword')

    def create(self):
        """POST /sword: Create a new item"""
        # url('sword')

    def new(self, format='html'):
        """GET /sword/new: Form to create a new item"""
        # url('new_sword')

    def update(self, id):
        """PUT /sword/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('sword', id=ID),
        #           method='put')
        # url('sword', id=ID)

    def delete(self, id):
        """DELETE /sword/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('sword', id=ID),
        #           method='delete')
        # url('sword', id=ID)

    def show(self, id, format='html'):
        """GET /sword/id: Show a specific item"""
        # url('sword', id=ID)

    def edit(self, id, format='html'):
        """GET /sword/id/edit: Form to edit an existing item"""
        # url('edit_sword', id=ID)
