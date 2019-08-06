#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time

# Pour l'internationalisation
import gettext
_ = gettext.gettext

setupconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

roue = setupconfig['Parametres']['roue']
aimants = setupconfig['Parametres']['aimants']
orientation = setupconfig['Parametres']['orientation']
lecture = setupconfig['Parametres']['lecture']
boutonsTrip = setupconfig['Parametres']['boutonsTrip']
boutonsRB = setupconfig['Parametres']['boutonsRB']

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
<h1>""")
print(_("Main settings"))
print("""</h1>
</div>

<!-- Table des reglages -->
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey">
<form action = "save_setup.py" method = "post">
   <div class="w3-row-padding">

""")
print('   <div class="w3-col m3">')
print('    <label>')
print(_("Wheelsize (mm)"))
print('</label>')
print('    <input type="text" id="roue" name="user_roue" value="{}" class="w3-input w3-border" placeholder="1864">'.format(roue))
print('  </div>')

print('   <div class="w3-col m3">')
print('    <label for="aimant">')
print(_("Magnet(s)"))
print('</label>')
print('    <input type="text" id="aimant" name="user_aimant" value={} class="w3-input w3-border" placeholder="1">'.format(aimants))
print('  </div>')

print('   <div class="w3-col m3">')
print('    <label for="orientation">')
print(_("Orientation"))
print('</label>')
print('    <select id="orientation" name="user_orientation" class="w3-select">')
if orientation == 'Paysage' :
  print('    <option selected="Paysage" value="Paysage">',_("Landscape"),'</option>')
  print('    <option value="Portrait">',_("Portrait"),'</option>')
else:
  print('    <option value="Paysage">',_("Landscape"),'</option>')
  print('    <option selected="Portrait" value="Portrait">',_("Portrait"),'</option>')
print('     </select>')
print('  </div>')

print('   <div class="w3-col m3">')
print('    <label for="lecture">')
print(_("Reading"))
print('</label>')
print('    <select id="lecture" name="user_lecture" class="w3-select">')
if lecture == 'BasEnHaut' :
  print('    <option selected="BasEnHaut" value="BasEnHaut">',_("From Bottom To Top"),'</option>')
  print('    <option value="HautEnBas">',_("From Top To Bottom"),'</option>')
else:
  print('    <option value="BasEnHaut">',_("From Bottom to Top"),'</option>')
  print('    <option selected="HautEnBas" value="HautEnBas">',_("From Top To Bottom"),'</option>')
print('     </select>')
print('  </div>')

print('  </div>')
print('<div class="w3-row-padding">')

print('   <div class="w3-col m3">')
print('    <label for="boutonsTrip">')
print(_("Trip Buttons"))
print('</label>')
print('    <select id="boutonsTrip" name="user_trip" class="w3-select">')
if boutonsTrip == '1' :
  print('    <option selected="1" value="1">',_("Left/OK/Right"),'</option>')
  print('    <option value="2">',_("Left/Right/OK"),'</option>')
else:
  print('    <option value="1">',_("Left/OK/Right"),'</option>')
  print('    <option selected="2" value="2">',_("Left/Right/OK"),'</option>')
print('     </select>')
print('  </div>')

print('   <div class="w3-col m3">')
print('    <label for="boutonsRB">')
print(_("RB Buttons"))
print('</label>')
print('    <select id="boutonsRB" name="user_rb" class="w3-select">')
if boutonsRB == '1' :
  print('    <option selected="1" value="1">',_("Up/Down"),'</option>')
  print('    <option value="2">',_("Down/Up"),'</option>')
else:
  print('    <option value="1">',_("Up/Down"),'</option>')
  print('    <option selected="2" value="2">',_("Down/Up"),'</option>')
print('     </select>')
print('  </div>')

print('  </div>')

print("""
<div class="w3-bar">
        <button class="w3-submit w3-btn w3-red w3-hover-teal w3-margin" type="submit">""")
print(_("OK"))
print("""</button>
</div>

</form>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge material-icons">web</i> """)
print(_("Screen setup"))
print('</a>  <a href="clock_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge fa fa-clock-o"></i> ')
print(_("Time Adjust"))
print('</a>  <a href="wifi_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge fa fa-wifi"></i> Wifi</a>')
print('<a href="warning_raz.py" class="w3-bar-item w3-button w3-right w3-hover-red" ><i class="w3-xlarge fa fa-undo"></i> ')
print(_("Factory Reset"))
print('</a>  <a href="warning_ota.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge material-icons">system_update</i> ')
print(_("Firmware Update"))
print("""</a>
</div>
</body>
</html>""")
