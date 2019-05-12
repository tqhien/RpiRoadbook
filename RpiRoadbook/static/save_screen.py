#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import configparser

# Pour l'internationalisation
import gettext
_ = gettext.gettext

nb_screens = 4

screenconfig = configparser.ConfigParser()

# On charge les reglages :
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/screen.cfg','/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/screen.cfg']
screenconfig.read(candidates)

print("Content-Type: text/html")
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
print(_('Configuration des &eacute;crans'))
print('</h1></div>')

for k in range (1,nb_screens+1) :
    jour_nuit = 'jour_nuit{}'.format(k)
    if jour_nuit in form:
        screenconfig['Affichage{}'.format(k)]['jour_nuit'] = form[jour_nuit].value
    layout = 'layout{}'.format(k)
    if layout in form:
        screenconfig['Affichage{}'.format(k)]['layout'] = form[layout].value
    for j in range (1,7) :
        champkj = 'champ{}{}'.format(k,j)
        if champkj in form:
            screenconfig['Affichage{}'.format(k)]['ligne{}'.format(j)] = form[champkj].value

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/screen.cfg', 'w') as configfile:
      screenconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    print('<h3>')
    print(_('Configuration sauvegard&eacute;e !'))
    print('</h3>')
    break
else :
  print('<h3>Write Error screen.cfg after 5 tries</h3>')

print ("""
<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>""")
print(_('Configuration'))
print('</a>  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge material-icons">web</i> ')
print(_('Personnalisation des &eacute;crans'))
print("""</a>
</div>
</body>
</html>""")
