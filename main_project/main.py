#!/usr/bin/env python3
"""Parse command line options and arguments for the Logic Simulator.

This script parses options and arguments specified on the command line, and
runs either the command line user interface or the graphical user interface.

Usage
-----
Show help: logsim.py -h
Command line user interface: logsim.py -c <file path>
Graphical user interface: logsim.py <file path>
"""
import getopt
import sys, os

import wx

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
from userint import UserInterface
from main_gui import Gui
from error import Error

#_________________IMPORTANT: CHANGE GUI MODULE________________#


# language domain
langDomain = "LOGIC SIM APP"
# languages you want to support
supLang = {u"en": wx.LANGUAGE_ENGLISH,
           u"fr": wx.LANGUAGE_FRENCH
          }


def _displayHook(obj):
    if obj is not None:
        print (repr(obj))

# add translation macro to builtin similar to what gettext does
import builtins
builtins.__dict__['_'] = wx.GetTranslation


from wx.lib.mixins.inspection import InspectionMixin

class BaseApp(wx.App, InspectionMixin):
    def OnInit(self):
        self.Init() # InspectionMixin
        # work around for Python stealing "_"
        sys.displayhook = _displayHook
        
        self.appName = "Logic Simulator"
        
        self.doConfig()

        print(wx.GetLocale())
        
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.updateLanguage(self.appConfig.Read(u"Language"))

        return True

    def doConfig(self):
        """Setup an application configuration file"""
        # configuration folder
        sp = wx.StandardPaths.Get()
        self.configLoc = sp.GetUserConfigDir()
        self.configLoc = os.path.dirname(os.path.abspath(__file__)) + "/" + self.appName

        if not os.path.exists(self.configLoc):
            os.mkdir(self.configLoc)

        # AppConfig stuff is here
        self.appConfig = wx.FileConfig(appName=self.appName,
                                       vendorName=u'Robbie Sewell, Lea Ganser-Potts, Daniel MacKinnon',
                                       localFilename=os.path.join(
                                       self.configLoc, "AppConfig"))
    
        if not self.appConfig.HasEntry(u'Language'):
            self.appConfig.Write(key=u'Language', value=u'fr')
            
        self.appConfig.Flush()

    def updateLanguage(self, lang):
        """
        Update the language to the requested one.
        
        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.
        
        :param string `lang`: one of the supported language codes
        
        """
        # if an unsupported language is requested default to English
        print(lang)
        if lang in supLang:
            selLang = supLang[lang]
        else:
            selLang = wx.LANGUAGE_ENGLISH
        print(selLang)
            
        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale
        
        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(langDomain)
        else:
            self.locale = None



app = BaseApp()
gui = Gui("Logic Simulator")
gui.Show(True)
app.MainLoop()

