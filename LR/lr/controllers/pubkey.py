import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
from lr.lib import signing

log = logging.getLogger(__name__)

class PubkeyController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('pubkey', 'pubkey')

    def index(self, format='text'):
        """GET /pubkey: All items in the collection"""
        # url('pubkey')
        response.headers["Content-Type"] =  "text/plain; charset=us-ascii"
        return signing.get_node_public_key()

    def create(self):
        """POST /pubkey: Create a new item"""
        response.headers["Content-Type"] =  "text/plain; charset=us-ascii"
        return signing.get_node_public_key()

    # def new(self, format='html'):
    #     """GET /pubkey/new: Form to create a new item"""
    #     # url('new_pubkey')

    # def update(self, id):
    #     """PUT /pubkey/id: Update an existing item"""
    #     # Forms posted to this method should contain a hidden field:
    #     #    <input type="hidden" name="_method" value="PUT" />
    #     # Or using helpers:
    #     #    h.form(url('pubkey', id=ID),
    #     #           method='put')
    #     # url('pubkey', id=ID)

    # def delete(self, id):
    #     """DELETE /pubkey/id: Delete an existing item"""
    #     # Forms posted to this method should contain a hidden field:
    #     #    <input type="hidden" name="_method" value="DELETE" />
    #     # Or using helpers:
    #     #    h.form(url('pubkey', id=ID),
    #     #           method='delete')
    #     # url('pubkey', id=ID)

    # def show(self, id, format='html'):
    #     """GET /pubkey/id: Show a specific item"""
    #     # url('pubkey', id=ID)

    # def edit(self, id, format='html'):
    #     """GET /pubkey/id/edit: Form to edit an existing item"""
    #     # url('edit_pubkey', id=ID)
