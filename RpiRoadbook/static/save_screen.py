#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import configparser
setupconfig = configparser.ConfigParser()
# Pour l'internationalisation
import gettext
_ = gettext.gettext
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


nb_screens = 4

screenconfig = configparser.ConfigParser()

# On charge les reglages :
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/screen.cfg','/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/screen.cfg']
screenconfig.read(candidates)

print("Content-Type: text/html")
print("""
<html>
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
print(_("Screen Settings"))
print('</h1></div>')

for k in range (1,nb_screens+1) :
    jour_nuit = 'jour_nuit{}'.format(k)
    if jour_nuit in form:
        screenconfig['Affichage{}'.format(k)]['jour_nuit'] = form[jour_nuit].value
    layout = 'layout{}'.format(k)
    if layout in form:
        screenconfig['Affichage{}'.format(k)]['layout'] = form[layout].value
    for j in range (1,7) :
        champkj = 'champ{}{}'.format(k,j)
        if champkj in form:
            screenconfig['Affichage{}'.format(k)]['ligne{}'.format(j)] = form[champkj].value
            print(screenconfig['Affichage{}'.format(k)]['ligne{}'.format(j)])

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/screen.cfg', 'w') as configfile:
      screenconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    print('<h3>')
    print(_("Settings saved !"))
    print('</h3>')
    break
else :
  print('<h3>Write Error screen.cfg after 5 tries</h3>')

print ("""
<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>""")
print(_("Setup"))
print('</a>  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge material-icons">web</i> ')
print(_("Screen Setup"))
print("""</a>
</div>
</body>
</html>""")
