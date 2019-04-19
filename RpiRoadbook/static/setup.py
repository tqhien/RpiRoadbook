#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time

setupconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

roue = setupconfig['Parametres']['roue']
aimants = setupconfig['Parametres']['aimants']
orientation = setupconfig['Parametres']['orientation']

datetime_now = time.localtime ()
st_date = '{}-{:02d}-{:02d}'.format(datetime_now.tm_year,datetime_now.tm_mon,datetime_now.tm_mday)
st_time = '{:02d}:{:02d}'.format(datetime_now.tm_hour,datetime_now.tm_min)


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
<hr>
<!-- Table des reglages -->
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey">
<form action = "save_setup.py" method = "post">
   <div class="w3-row-padding">

""")
print('   <div class="w3-third">')
print('    <label>Roue (en mm)</label>')
print('    <input type="text" id="roue" name="user_roue" value="{}" class="w3-input w3-border" placeholder="1864">'.format(roue))
print('  </div>')

print('   <div class="w3-third">')
print('    <label for="aimant">Aimant(s)</label>')
print('    <input type="text" id="aimant" name="user_aimant" value={} class="w3-input w3-border" placeholder="1">'.format(aimants))
print('  </div>')

print('   <div class="w3-third">')
print('    <label for="orientation">Orientation</label>')
print('    <select id="orientation" name="user_orientation" class="w3-select">')
if orientation == 'Paysage' :
  print('    <option selected="Paysage">Paysage</option>')
  print('    <option>Portrait</option>')
else:
  print('    <option>Paysage</option>')
  print('    <option selected="Portrait">Portrait</option>')
print('     </select>')
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
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue">Personnaliser les affichages</a>
  <a href="clock_setup.py" class="w3-bar-item w3-button w3-hover-blue">Ajuster l'horloge</a>
  <a href="raz.py" class="w3-bar-item w3-button w3-right w3-hover-red">Config. Usine</a>
  <a href="ota.py" class="w3-bar-item w3-button w3-right w3-hover-red">MAJ Firmware</a>
</div>

</body>
</html>""")
