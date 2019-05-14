#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

import configparser
setupconfig = configparser.ConfigParser()
# Pour l'internationalisation
import gettext
_ = gettext.gettext
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

en = gettext.translation('static', localedir='locales', languages=['en'])
it = gettext.translation('static', localedir='locales', languages=['it'])
de = gettext.translation('static', localedir='locales', languages=['de'])
es = gettext.translation('static', localedir='locales', languages=['es'])
langue = setupconfig['Parametres']['langue']
if langue == 'EN' :
    en.install()
    _ = en.gettext # English
elif langue == 'IT' :
    it.install()
    _ = it.gettext # Italiano
elif langue == 'DE' :
    de.install()
    _ = de.gettext
elif langue == 'ES' :
    es.install
    _ = es.gettext

print("""
<html>
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="w3.css">
	<link rel="stylesheet" href="font-awesome.min.css">
	<link rel="stylesheet" href="material-icons.css">
</head>
<body>
<!-- Entete -->
<div class="w3-container w3-center w3-section">
  <h1>""")
print(_('Configuration usine'))
print("""</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-blue w3-center">
   <h3>""")
print(_('Le retour &agrave; la configuration usine effacera vos personnalisations'))
print('</h3>   <h3>')
print(_("(Param&egrave;tres et personalisation d'&eacute;crans)"))
print('</h3>   <h3>')
print(_('Les roadbooks et leurs annotations sont cependant gard&eacute;s !'))
print('</h3>   <h3>')
print(_('Etes-vous s&ucirc;r de vouloir continuer ?'))
print("""</h3>
    <div class="w3-bar w3-margin">
      <a class="w3-bar-item w3-button w3-black w3-hover-blue w3-margin-right" href="index.py">""")
print(_("Annuler et revenir &agrave; l'accueil"))
print("""
  </a>      <a class="w3-bar-item w3-button w3-red w3-hover-orange w3-margin-left" href="raz.py" onclick="return confirm(' """)
print(_('Etes-vous s&ucirc;r ?'))
print(""" )');">""")
print(_('Continuer'))
print("""</a>
    </div>
</div>
<!-- Pied de page -->
<div class="w3-bar w3-black w3-margin">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>

</body>
</html>
""")
