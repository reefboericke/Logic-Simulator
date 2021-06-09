import sys
import os
import wx
import builtins


def set_language(app):
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

    locale.AddCatalogLookupPathPrefix('./locale')

    locale.AddCatalog('gui')
    if not locale.IsLoaded('gui'):
        print("Translation database failed to load.")
    return(locale)
