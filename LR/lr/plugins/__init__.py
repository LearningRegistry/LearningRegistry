
import imp, os, sys
from pylons import config
from yapsy.PluginManager import PluginManager
from yapsy import log, NormalizePluginNameForModuleName, IPlugin
from lr.plugins.tombstones import ITombstonePolicy, DoNotPublishError
import lr.loaded_plugins

__ALL__ = ["init_plugins", "LRPluginManager", "ITombstonePolicy", "DoNotPublishError"]



class CustomPackagePluginManager(PluginManager):
    PACKAGE_PREFIX = "lr.loaded_plugins."

    def loadPlugins(self, callback=None):
        """
        Load the candidate plugins that have been identified through a
        previous call to locatePlugins.  For each plugin candidate
        look for its category, load it and store it in the appropriate
        slot of the ``category_mapping``.

        If a callback function is specified, call it before every load
        attempt.  The ``plugin_info`` instance is passed as an argument to
        the callback.
        """
#       print "%s.loadPlugins" % self.__class__
        if not hasattr(self, '_candidates'):
            raise ValueError("locatePlugins must be called before loadPlugins")

        processed_plugins = []
        for candidate_infofile, candidate_filepath, plugin_info in self._candidates:
            # make sure to attribute a unique module name to the one
            # that is about to be loaded
            plugin_module_name_template = self.PACKAGE_PREFIX + NormalizePluginNameForModuleName( plugin_info.name) + "_%d"
            for plugin_name_suffix in range(len(sys.modules)):
                plugin_module_name =  plugin_module_name_template % plugin_name_suffix
                if plugin_module_name not in sys.modules:
                    break
            



            # tolerance on the presence (or not) of the py extensions
            if candidate_filepath.endswith(".py"):
                candidate_filepath = candidate_filepath[:-3]
            # if a callback exists, call it before attempting to load
            # the plugin so that a message can be displayed to the
            # user
            if callback is not None:
                callback(plugin_info)
            # cover the case when the __init__ of a package has been
            # explicitely indicated
            if "__init__" in  os.path.basename(candidate_filepath):
                candidate_filepath = os.path.dirname(candidate_filepath)
            try:
                # use imp to correctly load the plugin as a module
                if os.path.isdir(candidate_filepath):
                    candidate_module = imp.load_module(plugin_module_name,None,candidate_filepath,("py","r",imp.PKG_DIRECTORY))
                else:
                    with open(candidate_filepath+".py","r") as plugin_file:
                        candidate_module = imp.load_module(plugin_module_name,plugin_file,candidate_filepath+".py",("py","r",imp.PY_SOURCE))
            except Exception:
                exc_info = sys.exc_info()
                log.error("Unable to import plugin: %s" % candidate_filepath, exc_info=exc_info)
                plugin_info.error = exc_info
                processed_plugins.append(plugin_info)
                continue
            processed_plugins.append(plugin_info)
            if "__init__" in  os.path.basename(candidate_filepath):
                sys.path.remove(plugin_info.path)
            # now try to find and initialise the first subclass of the correct plugin interface
            for element in [getattr(candidate_module,name) for name in dir(candidate_module)]:
                plugin_info_reference = None
                for category_name in self.categories_interfaces:
                    try:
                        is_correct_subclass = issubclass(element, self.categories_interfaces[category_name])
                    except TypeError:
                        continue
                    if is_correct_subclass and element is not self.categories_interfaces[category_name]:
                            current_category = category_name
                            if candidate_infofile not in self._category_file_mapping[current_category]:
                                # we found a new plugin: initialise it and search for the next one
                                if not plugin_info_reference:
                                    plugin_info.plugin_object = element()
                                    plugin_info_reference = plugin_info
                                plugin_info.categories.append(current_category)
                                self.category_mapping[current_category].append(plugin_info_reference)
                                self._category_file_mapping[current_category].append(candidate_infofile)
        # Remove candidates list since we don't need them any more and
        # don't need to take up the space
        delattr(self, '_candidates')
        return processed_plugins




class __PluginManager(object):

    def __init__(self):
        self.manager = CustomPackagePluginManager()

        plugin_locations = config['app_conf']['lr.plugins'].split(':')

        self.manager.setPluginPlaces(plugin_locations)

        self.manager.setCategoriesFilter({
                ITombstonePolicy.ID: ITombstonePolicy
            })

        self.manager.collectPlugins()
 

    def activate(self):
        for pluginInfo in self.manager.getAllPlugins():
            if pluginInfo.plugin_object is not None:
                pluginInfo.plugin_object.activate()

    def deactivate(self):
        for pluginInfo in self.manager.getAllPlugins():
            if pluginInfo.plugin_object is not None:
                pluginInfo.plugin_object.deactivate()

    def getPlugins(self, category=None):
        if category is not None:
            for pluginInfo in self.manager.getPluginsOfCategory(category):
                yield pluginInfo.plugin_object

    def getPluginCount(self, category=None):
        if category is not None:
            return len(self.manager.getPluginsOfCategory(category))
        else:
            return 0

_LRPluginManager = None
def init_plugins():
    global _LRPluginManager

    if _LRPluginManager == None:
        _LRPluginManager = __PluginManager()
        _LRPluginManager.activate()

    return _LRPluginManager

LRPluginManager = init_plugins()





        

