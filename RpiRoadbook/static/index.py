#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re
import configparser

# Pour l'internationalisation
import gettext
_ = gettext.gettext

setupconfig = configparser.ConfigParser()
rbconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

en = gettext.translation('static', localedir='locales', languages=['en'])
#it = gettext.translation('rpiroadbook', localedir='locales', languages=['it'])
langue = setupconfig['Parametres']['langue']
if langue == 'EN' :
    en.install()
    _ = en.gettext # English

# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/RpiRoadbook.cfg','/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
rbconfig.read(candidates)

#files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files.sort()

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
print(_('Gestionnaire du RpiRoadbook'))
print("""</h1>
</div>

<!-- Choix mode -->
<div class="w3-container w3-section w3-topbar w3-bottombar w3-leftbar w3-rightbar w3-border-red">
<div class="w3-row">
	<div class="w3-col w3-light-grey s12 w3-center"><p><h3>""")
print(_('Changement de mode'))
print("""</h3></p></div>
</div>
<div class="w3-row">
		<!-- <div class="w3-col s12 m4 w3-red w3-center"><a class="w3-button w3-block" href="upload.html"><i class="w3-xlarge fa fa-map-signs"></i> Rallye</a></div> -->
""")
print('	<div class="w3-col s12 m4 w3-red w3-center w3-disabled">' if rbconfig['Mode']['mode']=='Rallye' else '	<div class="w3-col s12 m4 w3-red w3-center">')
print('<a class="w3-button w3-block" href="mode_rallye.py"><i class="w3-xlarge material-icons">call_split</i> ')
print(_('Rallye'))
print('</a></div>')
print('	<div class="w3-col s12 m4 w3-green w3-center w3-disabled">' if rbconfig['Mode']['mode']=='Route' else '	<div class="w3-col s12 m4 w3-green w3-center">')
print('<a class="w3-button w3-block" href="mode_route.py"><i class="w3-xlarge fa fa-tachometer"></i> ')
print(_('Route'))
print('</a></div>')
print('	<div class="w3-col s12 m4 w3-teal w3-center w3-disabled">' if rbconfig['Mode']['mode']=='Zoom' else '	<div class="w3-col s12 m4 w3-teal w3-center">')
print('<a class="w3-button w3-block" href="mode_zoom.py"><i class="w3-xlarge fa fa-search-plus"></i> ')
print(_('Zoom'))
print('</a></div>')
print("""
</div>
</div>

<!-- Table des rb presents -->
<div class="w3-container w3-section w3-topbar w3-bottombar w3-leftbar w3-rightbar w3-border-blue">
<form action="rm_rb.py" method="post">
<table class="w3-table-all">
<tr>
  <th></th>
  <th>""")
print(_('Nom du roadbook (clic pour annoter)'))
print("""</th>
</tr>
""")

for fileitem in files:
  print ('<tr><td><input class="w3-check" type="checkbox" name="choix" value="{}"></td><td><a class="w3-button w3-block w3-left-align" href="text_editor.py?fn={}"> {} </a></td>'.format(fileitem,fileitem,fileitem))

print ("""
</table>

<!-- Barre de edition -->
<div class="w3-bar w3-grey">
  <a href="upload.py" class="w3-bar-item w3-button w3-hover-blue"><i class="w3-xlarge fa fa-cloud-upload"></i> """)
print(_('Ajouter un Roadbook'))
print("""</a>
  <button class="w3-bar-item w3-submit w3-btn w3-hover-red" type="submit" onclick="return confirm(""")
print(_('Etes-vous s&ucirc;r de vouloir supprimer ?'))
print(');"><i class="w3-xlarge fa fa-trash"></i> ')
print(_('Supprimer les roadbooks s&eacute;lectionn&eacute;s'))
print("""</button>
</div>
</form>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="screen_setup.py"><i class="w3-xlarge material-icons">web</i> """)
print(_('Personnaliser les &eacute;crans'))
print('</a>')
print('  <a href="setup.py" class="w3-bar-item w3-button w3-right w3-hover-red"><i class="w3-xlarge fa fa-wrench"></i> ')
print(_('Configuration'))
print("""</a>
</div>
<div class="w3-bar">
  <a class="w3-bar-item" href="set_fr.py">FR</a>
  <a class="w3-bar-item" href="set_en.py">EN</a>
  <a class="w3-bar-item" href="set_it.py">IT</a>
  <a class="w3-bar-item" href="set_de.py">DE</a>
  <a class="w3-bar-item" href="set_es.py">ES</a>
</div>

</body>
</html>""")
