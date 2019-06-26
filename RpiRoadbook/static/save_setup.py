#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time
import subprocess

# Pour l'internationalisation
import gettext
_ = gettext.gettext

form = cgi.FieldStorage()

setupconfig = configparser.ConfigParser()
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

fr = gettext.translation('static', localedir='locales', languages=['fr'])
en = gettext.translation('static', localedir='locales', languages=['en'])
it = gettext.translation('static', localedir='locales', languages=['it'])
de = gettext.translation('static', localedir='locales', languages=['de'])
es = gettext.translation('static', localedir='locales', languages=['es'])
langue = setupconfig['Parametres']['langue']
if langue == 'FR' :
    fr.install()
    _ = fr.gettext # Francais
elif langue == 'EN' :
    en.install()
    _ = en.gettext # English
elif langue == 'IT' :
    it.install()
    _ = it.gettext # Italiano
elif langue == 'DE' :
    de.install()
    _ = de.gettext
elif langue == 'ES' :
    es.install
    _ = es.gettext

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
<h1>""")
print(_("Main Settings"))
print("""</h1>
</div>

<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey w3-margin">
<h3>""")
print(_("Settings saved :"))
print('</h3>')

if 'user_roue' in form:
  setupconfig['Parametres']['roue'] = form['user_roue'].value
  print (_("Wheelsize : {} mm").format(setupconfig['Parametres']['roue']))
  print('<br>')

if 'user_aimant' in form:
  setupconfig['Parametres']['aimants'] = form['user_aimant'].value
  print (_("Magnets : {}").format(setupconfig['Parametres']['aimants']))
  print('<br>')

if 'user_orientation' in form:
  setupconfig['Parametres']['orientation'] = form['user_orientation'].value
  print (_("Orientation : {}").format(setupconfig['Parametres']['orientation']))
  print('<br>')

if 'user_lecture' in form:
  setupconfig['Parametres']['lecture'] = form['user_lecture'].value
  print (_("Reading : {}").format(setupconfig['Parametres']['lecture']))
  print('<br>')

if 'user_trip' in form:
  setupconfig['Parametres']['boutonsTrip'] = form['user_trip'].value
  print (_("Trip Buttons, mode : {}").format(setupconfig['Parametres']['boutonsTrip']))
  print('<br>')

if 'user_rb' in form:
  setupconfig['Parametres']['boutonsRB'] = form['user_rb'].value
  print (_("RB Buttons, mode : {}").format(setupconfig['Parametres']['boutonsRB']))
  print('<br>')

if 'user_pull' in form:
  setupconfig['Parametres']['boutonsPull'] = form['user_pull'].value
  print (_("Pull Buttons : {}").format(setupconfig['Parametres']['boutonsPull']))
  print('<br>')

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
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge material-icons">web</i> """)
print(_("Screen setup"))
print('</a>  <a href="clock_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge fa fa-clock-o"></i> ')
print(_("Time adjust"))
print('</a>  <a href="warning_raz.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge fa fa-undo"></i> ')
print(_("Factory Reset"))
print('</a>  <a href="warning_ota.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge material-icons">system_update</i> ')
print(_("Firmware Update"))
print("""</a>
</div>
</body>
</html>
""")
