#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time
import subprocess

form = cgi.FieldStorage()

wificonfig = configparser.ConfigParser()
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/hostapd.conf','/home/rpi/RpiRoadbook/hostapd.conf','/mnt/piusb/.conf/hostapd.conf']
wificonfig.read(candidates)

#roue = setupconfig['Parametres']['roue']
#aimants = setupconfig['Parametres']['aimants']

st_date = ''
st_time = ''

print ('Content-Type: text/html\n')
print ("""<html>
<head>
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
<h3>Configuration WIFI sauvegard&eacute;e :</h3>
""")

if 'user_ssid' in form:
  wificonfig['ssid'] = form['user_ssid'].value
  print ("SSID : {} <br>".format(wificonfig['ssid']))

if 'user_passphrase' in form:
  wificonfig['wpa_passphrase'] = form['user_passphrase'].value
  print ("Mot de passe : {}<br>".format(wificonfig['wpa_passphrase']))

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/hostapd2.conf', 'w') as configfile:
      wificonfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    break
else :
  print('Write Error hostapd2.conf after 5 tries\n')

print ("""
<br>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge fa fa-wrench"></i>Configurer</a>
</div>
</body>
</html>
""")
