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
candidates = ['/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
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
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Configuration g&eacute;n&eacute;rale</h1>
<hr>
<h3>Configuration sauvegard&eacute;e :</h3>
""")

if 'user_roue' in form:
  setupconfig['Parametres']['roue'] = form['user_roue'].value
  print ("Roue : {} mm\n".format(setupconfig['Parametres']['roue']))

if 'user_aimant' in form:
  setupconfig['Parametres']['aimants'] = form['user_aimant'].value
  print ("Nb aimants : {}\n".format(setupconfig['Parametres']['aimants']))

if 'user_orientation' in form:
  setupconfig['Parametres']['orientation'] = form['user_orientation'].value
  print ("Orientation : {}\n".format(setupconfig['Parametres']['orientation']))

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

print ("""
<hr>
<a href="index.py"> <input type="button" value="Accueil"> </a>
</div>
</body>
</html>
""")
