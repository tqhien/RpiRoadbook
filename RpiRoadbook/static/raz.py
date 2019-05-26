#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import shutil

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


print ("""Content-Type: text/html\n
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
print(_("Retour &agrave la configuration d'usine"))
print("""</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey w3-margin">
<h3>""")
print(_('Fichiers supprim&eacute;s :'))
print('</h3>')

filelist = [
    '.conf/RpiRoadbook.cfg',
    '.conf/RpiRoadbook_setup.cfg',
    '.conf/route.cfg',
    '.conf/screen.cfg',
    '.conf/hostapd.conf',
    '.log/chrono.cfg',
    '.log/odo.cfg',
]

for fileitem in filelist:
    try:
        os.remove("/mnt/piusb/{}".format(fileitem))
    except :
        pass
    else:
        print('{}<br>'.format(fileitem))
print ("""
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>""")
print(_('Configurer'))
print("""</a>
</div>
</body>
</html>""")
