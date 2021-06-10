"""Called by logsim.py to set up language of GUI as it's built."""
import sys
import os
import wx
import builtins
import locale
import ctypes

def set_language(app):
    """Set language of the GUI by checking command line and OS."""
    language = wx.LANGUAGE_DEFAULT
    if sys.platform.capitalize() in ('Linux', 'Darwin'):
        lang = os.environ['LANG']
        if lang in ('de_DE.utf8', 'de_DE.UTF-8'):
            # if unix and langauge flag set
            language = wx.LANGUAGE_GERMAN
        else:
            print("Defaulting to English operation.")
    else:
        # windows environmnent
        windll = ctypes.windll.kernel32
        windll.GetUserDefaultUILanguage()
        OS_language = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
        if OS_language == 'de_DE':
            # this is captured by default anyway but make it explicit
            # for logic check below
            language = wx.LANGUAGE_GERMAN
        else:
            print("Defaulting to English operation.")

    builtins._ = wx.GetTranslation

    if language == wx.LANGUAGE_GERMAN:
        wxlocale = wx.Locale()
        wxlocale.Init(language)
        # if loading German, check it happens correctly
        wxlocale.AddCatalogLookupPathPrefix('./locale')
        wxlocale.AddCatalog('gui')
        if not wxlocale.IsLoaded('gui'):
            print("Translation database failed to load - using English instead.")

        return(wxlocale)

    return(None)
