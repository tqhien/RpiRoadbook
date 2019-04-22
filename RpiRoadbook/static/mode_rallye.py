#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re
import configparser

setupconfig = configparser.ConfigParser()
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/RpiRoadbook.cfg','/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
setupconfig.read(candidates)

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
<h1>Changement de mode</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey w3-margin">
<h3>Nouveau mode :</h3>
""")

setupconfig['Mode']['mode'] = 'Rallye'

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/RpiRoadbook.cfg', 'w') as configfile:
      setupconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    print ('<h3>Rallye</h3>')
    break
else :
  print('Write Error RpiRoadbook.cfg after 5 tries')

print("""
Attendez 5 secondes et red&eacute;marrez le RpiRoadbook
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>Configurer</a>
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue">Personnaliser les affichages</a>
</div>
</body>
</html>""")
