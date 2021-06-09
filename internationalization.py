"""Called by logsim.py to set up language of GUI as its built."""
import sys
import os
import wx
import builtins


def set_language(app):
    """Set language of the GUI by checking command line and OS."""
    language = wx.LANGUAGE_DEFAULT
    if sys.platform.capitalize() in ('Linux', 'Darwin'):
        if os.environ['LANG'] == 'de_DE.utf8':
            # if unix and langauge flag set
            language = wx.LANGUAGE_GERMAN
        else:
            print("Defaulting to English operation.")
    builtins._ = wx.GetTranslation
    locale = wx.Locale()
    locale.Init(language)

    # if loading German, check it happens correctly
    locale.AddCatalogLookupPathPrefix('./locale')
    locale.AddCatalog('gui')
    if not locale.IsLoaded('gui'):
        print("Translation database failed to load.")
    return(locale)
