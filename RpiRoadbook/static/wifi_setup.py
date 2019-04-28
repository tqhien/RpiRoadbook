#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time

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

print("""<html>
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

<!-- Table des reglages -->
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey">
<form action = "save_wifi.py" method = "post">
   <div class="w3-row-padding">

""")
print('   <div class="w3-half">')
print('    <label>R&eacute;seau wifi (SSID) :</label>')
print('    <input type="text" id="roue" name="user_ssid" value="{}" class="w3-input w3-border" placeholder="rpirb_custom">'.format(ssid))
print('  </div>')

print('   <div class="w3-half">')
print('    <label for="passphrase">Mot de passe : </label>')
print('    <input type="text" id="user_passphrase" name="user_passphrase" value={} class="w3-input w3-border" placeholder="rpiroadbook">'.format(wpa_passphrase))
print('  </div>')

print("""
<div class="w3-bar">
        <button class="w3-submit w3-btn w3-red w3-hover-teal w3-margin" type="submit">Valider</button>
</div>
</div>
</form>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge fa fa-wrench"></i>Configurer</a>
</div>

</body>
</html>""")
