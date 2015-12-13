import sys
import os
import xbmc
import xbmcaddon

__scriptid__   = "script.linux.wicd"
__addon__       = xbmcaddon.Addon(id=__scriptid__)
__version__     = __addon__.getAddonInfo('version')
__id__          = __addon__.getAddonInfo('id')
__cwd__         = __addon__.getAddonInfo('path')
__language__    = __addon__.getLocalizedString

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

print "[SCRIPT] '%s: version %s' initialized!" % (__id__, __version__, )

if (__name__ == "__main__"):
    import gui
    ui = gui.GUI( "script_linux_wicd-main.xml" , __cwd__ , "default",msg='', first=True)
    del ui

sys.modules.clear()