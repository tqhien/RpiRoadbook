#!/usr/bin/python
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import re

import time

import subprocess

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


print ('Content-Type: text/html\n')
print ("""
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
print(_('Mise &agrave; jour de firmware'))
print("""</h1>
  </div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-red">
<div class="w3-row">
<div class="w3-col w3-light-grey s12 w3-center">
""")


if 'filename' in form:
  # On recupere le nom de fichier
  fileitem = form['filename']
  # Test si le fichier a bien ete telecharge
  if fileitem.filename:
    open('/mnt/piusb/ota/ota.tar.gz', 'wb').write(fileitem.file.read())
    # On attend au moins 5 secondes, le temps que le cache btrfs soit mis sur disque
    time.sleep (6.0)
    print('<h3>')
    print(_('Firmware t&eacute;l&eacute;charg&eacute;.'))
    print('</h3><br>')
    print('<h3>')
    print(_('Red&eacute;marrez le RpiRoadbook'))
    print('</h3><br>')
    print('<h3>')
    print(_('pour appliquer la mise &agrave; jour.'))
    print('</h3><br>')
print("""
</div>
</div>
</div>
  <!-- Pied de page -->
  <div class="w3-bar w3-black">
    <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  </div>
  </body>
  </html>
""")
