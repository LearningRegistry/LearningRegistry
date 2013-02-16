from yapsy.IPlugin import IPlugin
import traceback
class BasePlugin(IPlugin):
    
    def __init__(self):
        super(BasePlugin, self).__init__()


    def activate(self):
        super(BasePlugin, self).activate()
        print "#################### Activated %s ####################\n" % self.__class__.__name__


    def deactivate(self):
        super(BasePlugin, self).deactivate()
        print "#################### Deactivated %s ####################\n" % self.__class__.__name__
