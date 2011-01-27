import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class DescriptionController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('description', 'description')

    def index(self, format='html'):
        """GET /description: All items in the collection"""
        import urllib2, json, time, os
        url = 'http://localhost:5984/node/description'
        response = urllib2.urlopen(url)
        data = json.load(response)
        data['timestamp'] = time.asctime()
        return json.dumps(data)
        # url('description')

    def create(self):
        """POST /description: Create a new item"""
        # url('description')

    def new(self, format='html'):
        """GET /description/new: Form to create a new item"""
        # url('new_description')

    def update(self, id):
        """PUT /description/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('description', id=ID),
        #           method='put')
        # url('description', id=ID)

    def delete(self, id):
        """DELETE /description/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('description', id=ID),
        #           method='delete')
        # url('description', id=ID)

    def show(self, id, format='html'):
        """GET /description/id: Show a specific item"""
        # url('description', id=ID)

    def edit(self, id, format='html'):
        """GET /description/id/edit: Form to edit an existing item"""
        # url('edit_description', id=ID)
