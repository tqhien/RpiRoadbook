#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time

setupconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/rpi/RpiRoadbook/default.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

roue = setupconfig['Parametres']['roue']
aimants = setupconfig['Parametres']['aimants']
orientation = setupconfig['Parametres']['orientation']
mode = setupconfig['Parametres']['mode']
mode_jour = setupconfig['Parametres']['jour_nuit']
luminosite = setupconfig['Parametres']['luminosite']

datetime_now = time.localtime ()
st_date = '{}-{:02d}-{:02d}'.format(datetime_now.tm_year,datetime_now.tm_mon,datetime_now.tm_mday)
st_time = '{:02d}:{:02d}'.format(datetime_now.tm_hour,datetime_now.tm_min)


print('<html>')
print('<body>')
print('   <form action = "save_setup.py" method = "post">')

print('  <div>')
print('    <label for="mode">Mode:</label>')
print('    <select id="mode" name="user_mode">')
if mode == 'Rallye' :
  print('    <option selected="Rallye">Rallye</option>')
  print('    <option>Route</option>')
  print('    <option>Zoom</option>')
elif mode == 'Route':
  print('    <option>Rallye</option>')
  print('    <option selected="Route">Route</option>')
  print('    <option>Zoom</option>')
elif mode == 'Zoom' :
  print('    <option>Rallye</option>')
  print('    <option>Route</option>')
  print('    <option selected="Zoom">Zoom</option>')
print('     </select>')
print('  </div>')

print('  <div>')
print('    <label for="mode_jour">Jour/Nuit</label>')
print('    <select id="mode_jour" name="user_jour">')
if mode_jour == 'Jour' :
  print('    <option selected="Jour">Jour</option>')
  print('    <option>Nuit</option>')
else:
  print('    <option>Jour</option>')
  print('    <option selected="Nuit">Nuit</option>')
print('     </select>')
print('  </div>')

print('   <div>')
print('    <label for="luminosite">Luminosite:</label>')
print('    <input type="text" id="luminosite" name="user_luminosite" value={}> %'.format(luminosite))
print('  </div>')

print('  <div>')
print('    <label for="orientation">Orientation</label>')
print('    <select id="orientation" name="user_orientation">')
if orientation == 'Paysage' :
  print('    <option selected="Paysage">Paysage</option>')
  print('    <option>Portrait</option>')
else:
  print('    <option>Paysage</option>')
  print('    <option selected="Portrait">Portrait</option>')
print('     </select>')
print('  </div>')

print('<br>')

print('   <div>')
print('    <label for="roue">Roue:</label>')
print('    <input type="text" id="roue" name="user_roue" value={}> mm'.format(roue))
print('  </div>')

print('   <div>')
print('    <label for="aimant">Aimant(s):</label>')
print('    <input type="text" id="aimant" name="user_aimant" value={}>'.format(aimants))
print('  </div>')

print('   <div>')
print('    <label for="date">Date:</label>')
print('    <input type="date" id="date" name="user_date" value={}'.format(st_date))
print ('pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}">')
print('  </div>')

print('   <div>')
print('    <label for="time">Heure:</label>')
print('    <input type="time" id="time" name="user_time" value={}'.format(st_time))
print ('pattern="[0-9]{2}:[0-9]{2}">')
print('  </div>')

print('   <input type = "submit" value = "Valider" /></p>')
print('   </form>')
print('<a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>')
print('</body>')
print('</html>')
