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
candidates = ['/home/rpi/RpiRoadbook/default.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
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
print ("<html>")
print ("<body>")
print ("<h1>Configuration sauvegard&eacute;e :</h1>")

if 'user_mode' in form:
  setupconfig['Parametres']['mode'] = form['user_mode'].value
  print (setupconfig['Parametres']['mode'])  

if 'user_jour' in form:
  setupconfig['Parametres']['jour_nuit'] = form['user_jour'].value
  print (setupconfig['Parametres']['jour_nuit'])
  
if 'user_luminosite' in form:
  setupconfig['Parametres']['luminosite'] = form['user_luminosite'].value
  print (setupconfig['Parametres']['luminosite'])
  
if 'user_orientation' in form:
  setupconfig['Parametres']['orientation'] = form['user_orientation'].value
  print (setupconfig['Parametres']['orientation'])
  
if 'user_roue' in form:
  setupconfig['Parametres']['roue'] = form['user_roue'].value
  print (setupconfig['Parametres']['roue'])
  
if 'user_aimant' in form:
  setupconfig['Parametres']['aimants'] = form['user_aimant'].value
  print (setupconfig['Parametres']['aimants'])

if 'user_date' in form:
  st_date = form['user_date'].value
  print (st_date)
  
if 'user_time' in form:
  st_time = form['user_time'].value
  print (st_time)

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
  print('Write Error RpiRoadbook_setup.cfg after 5 tries')

print ("</body>")
print ("</html>")
  
