import logging, json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from lr.lib.base import BaseController, render
import urllib2

log = logging.getLogger(__name__)

class FiltersController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('filter', 'filters', controller='contrib/filters', 
    #         path_prefix='/contrib', name_prefix='contrib_')

    def index(self, format='json'):
        """GET /contrib/filters: All items in the collection"""
        url = 'http://localhost:5984/resource_data/_design/filter'
        res = urllib2.urlopen(url);
        response.headers['content-type'] = 'text/javascript'
        
        design = json.load(res)
        
        filters = { "filters": design["views"].keys() }
        return json.dumps(filters);
        # url('contrib_filters')

    def create(self):
        """POST /contrib/filters: Create a new item"""
        # url('contrib_filters')

    def new(self, format='html'):
        """GET /contrib/filters/new: Form to create a new item"""
        # url('contrib_new_filter')

    def update(self, id):
        """PUT /contrib/filters/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('contrib_filter', id=ID),
        #           method='put')
        # url('contrib_filter', id=ID)

    def delete(self, id):
        """DELETE /contrib/filters/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('contrib_filter', id=ID),
        #           method='delete')
        # url('contrib_filter', id=ID)

    def show(self, id, format='json'):
        """GET /contrib/filters/id: Show a specific item"""
        url = 'http://127.0.0.1:5984/resource_data/_design/filter/_view/'+id
        res = urllib2.urlopen(url);
        response.headers['content-type'] = 'text/javascript'
        return res.read()
        # url('contrib_filter', id=ID)

    def edit(self, id, format='json'):
        """GET /contrib/filters/id/edit: Form to edit an existing item"""
        url = 'http://localhost:5984/resource_data/_design/filter'
        res = urllib2.urlopen(url);
        response.headers['content-type'] = 'text/javascript'
        
        design = json.load(res)
        
        filters = { id : design["views"][id] }
        return json.dumps(filters);
        # url('contrib_edit_filter', id=ID)
