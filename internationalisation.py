import sys
import os
import wx
import builtins

def set_language(app):
    if sys.platform.capitalize() in ('Linux', 'Darwin'):
        if os.environ['LANG'] == 'de_DE.utf8':
            # if unix and langauge flag set
            language = wx.LANGUAGE_GERMAN
        else:
            language = wx.LANGUAGE_DEFAULT
    else:
        # no flag / windows system
        language = wx.LANGUAGE_DEFAULT
    builtins._ = wx.GetTranslation
    locale = wx.Locale()
    locale.Init(language)
    
    locale.AddCatalogLookupPathPrefix('./locale')

    locale.AddCatalog('gui')
    print(locale.IsLoaded('gui'))
    return(locale)