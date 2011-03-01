import ConfigParser, os
import couchdb
import sys
import json

_config = ConfigParser.ConfigParser()
_config.read('../LR/development.ini')

_SERVER_URL = _config.get("app:main", "couchdb.url")
_RESOURCE_DATA = _config.get("app:main", "couchdb.dbname")

_couchServer = couchdb.Server(url=_SERVER_URL)

def CreateDB():
    '''Creates a DB in Couch based upon config'''
    try:
        _couchServer[_RESOURCE_DATA]
        stats = _couchServer.stats()
        s = json.dumps(stats, sort_keys=True, indent=4)
        prettyStats = '\n'.join([l.rstrip() for l in s.splitlines()])
        print("DB Exists, Here are some stats: {0}".format(prettyStats))
    except couchdb.http.ResourceNotFound as rnf:
        print("DB '{0}' doesn't exist on '{1}', creating\n".format(_RESOURCE_DATA, _SERVER_URL))
        try:
            _couchServer.create(_RESOURCE_DATA)
            print("Created DB '{0}' on '{1}'\n".format(_RESOURCE_DATA, _SERVER_URL))
    
        except Exception as e:
            print("Exception while creating database: {0}\n".format(e) )

if __name__ == "__main__":
    CreateDB()

