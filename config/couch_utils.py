'''
Created on Aug 18, 2011

@author: jklo
'''
from couchapp import config as cfg, commands as cmd
import logging, os
import sys

log = logging.getLogger(__name__)

def pushCouchApp(sourceDir, destURL):
    try:
        conf = cfg.Config()
        cmd.push(conf, sourceDir, destURL)
        print("Deployed CouchApp from '{0}' to '{1}'".format(sourceDir, destURL))
    except:
        print repr(sys.exc_info())
        print("Unable to push CouchApp at '{0}'".format(sourceDir))


def pushAllCouchApps(sourceDirPath, couchDBURL):
    for db_name in os.listdir(sourceDirPath):
        destURL = "{0}/{1}".format(couchDBURL, db_name)
        appsPath = os.path.join(sourceDirPath, db_name, 'apps')
        if os.path.exists(appsPath) and os.path.isdir(appsPath):
            for app in os.listdir(appsPath):
                appDir = os.path.join(appsPath, app)
                if os.path.isdir(appDir):
                    pushCouchApp(appDir, destURL)
                    
        




if __name__ == "__main__":
    from setup_utils import getInput
    
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    
    def doesNotEndInSlash(input=None):
        return input is not None and input[-1] != "/"
    
    def dirExists(input=None):
        return input is not None and os.path.exists(input) and os.path.isdir(input)
    
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    defaultPath = os.path.join(scriptPath, "..", "couchdb")
    
    couchDBUrl = getInput("Enter your couchDB server URL", "http://127.0.0.1:5984", doesNotEndInSlash)
        
    couchApps = getInput("Enter the base directory to the CouchApps", defaultPath, dirExists)
    
    pushAllCouchApps(couchApps, couchDBUrl)
    
    
    
