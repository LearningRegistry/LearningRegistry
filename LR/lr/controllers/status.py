import logging

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render

log = logging.getLogger(__name__)

class StatusController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('status', 'status')

    def index(self, format='html'):
        """GET /status: All items in the collection"""
        import urllib2, json, time, os
        url = 'http://localhost:5984/node/status'
        response = urllib2.urlopen(url)
        data = json.load(response)
        data['timestamp'] = time.asctime()
        data['start_time'] = os.system('who -b')
        return json.dumps(data)
        # url('status')

    def create(self):
        """POST /status: Create a new item"""
        # url('status')

    def new(self, format='html'):
        """GET /status/new: Form to create a new item"""
        # url('new_status')

    def update(self, id):
        """PUT /status/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('status', id=ID),
        #           method='put')
        # url('status', id=ID)

    def delete(self, id):
        """DELETE /status/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('status', id=ID),
        #           method='delete')
        # url('status', id=ID)

    def show(self, id, format='html'):
        """GET /status/id: Show a specific item"""
        # url('status', id=ID)

    def edit(self, id, format='html'):
        """GET /status/id/edit: Form to edit an existing item"""
        # url('edit_status', id=ID)
