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
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Configuration g&eacute;n&eacute;rale</h1>
<hr>
   <form action = "save_setup.py" method = "post">
   <table style="width:100%">
""")
print('   <tr>')
print('    <td><label for="roue"><h3>Roue:</h3></label></td>')
print('    <td><input type="text" id="roue" name="user_roue" value={}> mm</td>'.format(roue))
print('  </tr>')

print('   <tr>')
print('    <td><label for="aimant"><h3>Aimant(s):</h3></label></td>')
print('    <td><input type="text" id="aimant" name="user_aimant" value={}></td>'.format(aimants))
print('  </tr>')

print('   <tr>')
print('    <td><label for="orientation"><h3>Orientation</h3></label></td>')
print('    <td><select id="orientation" name="user_orientation">')
if orientation == 'Paysage' :
  print('    <option selected="Paysage">Paysage</option>')
  print('    <option>Portrait</option>')
else:
  print('    <option>Paysage</option>')
  print('    <option selected="Portrait">Portrait</option>')
print('     </select></td>')
print('  </tr>')
print("""
</table>
<br>
<input type="submit" value="Valider"/></p>
   </form>
<hr>
<div>
<a href="screen_setup.py"> <input type="button" value="Personnaliser les affichages"></a>
<a href="clock_setup.py"> <input type="button" value="Ajuster l'horloge"></a>
<a href="raz.py"> <input type="button" value="Config. Usine"></a>
</div>
<hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
</div>
</body>
</html>""")
