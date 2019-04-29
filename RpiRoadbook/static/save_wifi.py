#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time
import subprocess

form = cgi.FieldStorage()

wificonfig = configparser.ConfigParser()

# On charge les reglages wifi
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/hostapd.conf','/home/rpi/RpiRoadbook/hostapd.conf','/mnt/piusb/.conf/hostapd.conf']
for i in candidates :
    try:
        with open(i, 'r') as f:
            config_string = '[dummy_section]\n' + f.read()
        wificonfig.read_string(config_string)
    except:
        pass

ssid = wificonfig['dummy_section']['ssid']
wpa_passphrase = wificonfig['dummy_section']['wpa_passphrase']

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
  wificonfig['dummy_section']['ssid'] = form['user_ssid'].value
  print ("SSID : {} <br>".format(wificonfig['dummy_section']['ssid']))

if 'user_passphrase' in form:
  wificonfig['dummy_section']['wpa_passphrase'] = form['user_passphrase'].value
  print ("Mot de passe : {}<br>".format(wificonfig['dummy_section']['wpa_passphrase']))

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/hostapd.conf', 'w') as configfile:
      for i in wificonfig.options('dummy_section') :
          configfile.write('{}={}\n'.format(i,wificonfig['dummy_section'][i]))
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    break
else :
  print('Write Error hostapd.conf after 5 tries\n')

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
