#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re
import configparser

# Pour l'internationalisation
import gettext
_ = gettext.gettext


setupconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)
setupconfig['Parametres']['langue'] = 'IT'

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/RpiRoadbook_setup.cfg', 'w') as configfile:
      setupconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    break
else :
  print('Write Error RpiRoadbook_setup.cfg after 5 tries\n')

it = gettext.translation('static', localedir='locales', languages=['it'])
langue = setupconfig['Parametres']['langue']
if langue == 'IT' :
    it.install()
    _ = it.gettext # English

print ('Content-Type: text/html\n')
print ("""<html>
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="w3.css">
	<link rel="stylesheet" href="font-awesome.min.css">
	<link rel="stylesheet" href="material-icons.css">
    <meta http-equiv="refresh" content="5; URL=index.py">
</head>
<body>
<!-- Entete -->
<div class="w3-container w3-center w3-section">
<h1>""")
print(_('Configuration de la langue'))
print("""</h1>
</div>

<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey w3-margin">
<h3>""")
print(_('Langue modifi&eacute;e : {}.').format(setupconfig['Parametres']['langue']))
print(_("Retour &agrave; l'accueil dans 5 secondes"))
print('</h3>')

print ("""
<br>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge material-icons">web</i> """)
print(_('Personnaliser les affichages'))
print('</a>  <a href="clock_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge fa fa-clock-o"></i> ')
print(_("Ajuster l'horloge"))
print('</a>  <a href="warning_raz.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge fa fa-undo"></i> ')
print(_('Config. Usine'))
print('</a>  <a href="warning_ota.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge material-icons">system_update</i> ')
print(_('MAJ Firmware'))
print("""</a>
</div>
<div class="w3-bar">
  <a class="w3-bar-item" href="set_fr.py">FR</a>
  <a class="w3-bar-item" href="set_en.py">EN</a>
  <a class="w3-bar-item" href="set_it.py">IT</a>
  <a class="w3-bar-item" href="set_de.py">DE</a>
  <a class="w3-bar-item" href="set_es.py">ES</a>
</div>
</body>
</html>
""")
