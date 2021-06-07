""" for keeping different implementations of functions in case decide to use them again """

"""
while( self.current_character.isspace() ):
    if self.current_character == '\n':
        self.last_EOL = self.file.tell()
        self.no_EOL += 1
    self.advance()
"""

""" 
if self.current_character == '#':  # comment found
    self.advance()
    while self.current_character != '#':
        self.advance()
    self.advance()
    self.get_symbol()
"""

"""
def is_punctuation(self):
         #Checks if current char is puncutation such
          #  that it isn't skipped over
        if self.current_character in [':', ';', '.']:
            return True
"""

"""
                elif inside_comment = True and self.current_character == '#':
                    # comment was never closed
                    self.unclosed_comment = True
                """


"""
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
localedir = os.path.join(basepath, "locale")
langid = LANGUAGE_GERMAN    # use OS default; or use LANGUAGE_JAPANESE, etc.
domain = "gui"
"""


"""
locale = wx.Locale()
locale.AddCatalogLookupPathPrefix('./locale')
locale.Init(wx.LANGUAGE_GERMAN)
locale.AddCatalog('de.po')

self.presLan_de = gettext.translation("gui", "./locale", languages=['de'])
self.presLan_de.install()
self.locale = wx.Locale(LANGUAGE_GERMAN)
locale.setlocale(locale.LC_ALL, 'de')
"""

""" MINE THAT WORKS
gettext.install('gui', './locale')
mylocale = wx.Locale()
mylocale.Init(langid)

mytranslation = gettext.translation(domain, localedir,
[mylocale.GetCanonicalName()], fallback = True)
mytranslation.install()

mylocale.AddCatalogLookupPathPrefix(localedir)
mylocale.AddCatalog(domain)
_ = wx.GetTranslation
wx.Log.AddTraceMask('i18n')
print(mylocale.IsLoaded('gui'))
"""

#builtins._ = wx.GetTranslation


#wx.Log.AddTraceMask('i18n')

#print(platform.system())
