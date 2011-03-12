'''
Copyright 2011 SRI International

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on Mar 10, 2011

@author: jklo
'''
import couchdb
from lr.lib.base import render
from lr.lib.harvest import harvest

class oaipmh(harvest):
    '''
    Utility class to provide OAI-PMH results from Learning Registy
    '''


    def __init__(self, server="http://localhost:5984", database="resource_data"):
        '''
        Constructor
        '''
        server = couchdb.Server(server)
        self.db = server[database]
        


    
if __name__ == "__main__":
    pass