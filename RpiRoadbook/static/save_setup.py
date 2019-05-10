#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time
import subprocess

form = cgi.FieldStorage()

setupconfig = configparser.ConfigParser()
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

#roue = setupconfig['Parametres']['roue']
#aimants = setupconfig['Parametres']['aimants']
#orientation = setupconfig['Parametres']['orientation']
#mode = setupconfig['Parametres']['mode']
#mode_jour = setupconfig['Parametres']['jour_nuit']
#luminosite = setupconfig['Parametres']['luminosite']

st_date = ''
st_time = ''

print ('Content-Type: text/html\n')
print ("""<html>
<head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<link rel="stylesheet" href="w3.css">
	<link rel="stylesheet" href="font-awesome.min.css">
	<link rel="stylesheet" href="material-icons.css">
</head>
<body>
<!-- Entete -->
<div class="w3-container w3-center w3-section">
<h1>Configuration g&eacute;n&eacute;rale</h1>
</div>

<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey w3-margin">
<h3>Configuration sauvegard&eacute;e :</h3>
""")

if 'user_roue' in form:
  setupconfig['Parametres']['roue'] = form['user_roue'].value
  print ("Roue : {} mm<br>".format(setupconfig['Parametres']['roue']))

if 'user_aimant' in form:
  setupconfig['Parametres']['aimants'] = form['user_aimant'].value
  print ("Nb aimants : {}<br>".format(setupconfig['Parametres']['aimants']))

if 'user_orientation' in form:
  setupconfig['Parametres']['orientation'] = form['user_orientation'].value
  print ("Orientation : {}<br>".format(setupconfig['Parametres']['orientation']))

if 'user_lecture' in form:
  setupconfig['Parametres']['lecture'] = form['user_lecture'].value
  print ("Sens de lecture : {}<br>".format(setupconfig['Parametres']['lecture']))

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

if setupconfig['Parametres']['orientation'] == 'Paysage' :
    subprocess.Popen('/home/rpi/RpiRoadbook/paysage.sh',shell=True)
else :
    subprocess.Popen('/home/rpi/RpiRoadbook/portrait.sh',shell=True)

print ("""
<br>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge material-icons">web</i> Personnaliser les affichages</a>
  <a href="clock_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge fa fa-clock-o"></i> Ajuster l'horloge</a>
  <a href="warning_raz.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge fa fa-undo"></i> Config. Usine</a>
  <a href="warning_ota.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge material-icons">system_update</i> MAJ Firmware</a>
</div>
</body>
</html>
""")
