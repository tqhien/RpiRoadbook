#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re
import configparser

setupconfig = configparser.ConfigParser()
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/RpiRoadbook.cfg','/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
setupconfig.read(candidates)

#files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files.sort()

print ('Content-Type: text/html\n')
print ("""<html>
<head>
<meta name="viewport" content="initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Gestionnaire du RpiRoadbook</h1>
<hr>
""")
print('<h3>Mode actuel : {}</h3>'.format(setupconfig['Mode']['mode']))
print('<a href="mode_rallye.py"> <input type="button" value="->Rallye" disabled></a>' if setupconfig['Mode']['mode']=='Rallye' else '<a href="mode_rallye.py"> <input type="button" value="->Rallye"></a>')
print('<a href="mode_route.py"> <input type="button" value="->Route" disabled></a>' if setupconfig['Mode']['mode']=='Route' else '<a href="mode_route.py"> <input type="button" value="->Route"></a>')
print('<a href="mode_zoom.py"> <input type="button" value="->Zoom" disabled></a>' if setupconfig['Mode']['mode']=='Zoom' else '<a href="mode_zoom.py"> <input type="button" value="->Zoom"></a>')
print("""
<hr>
<h3>Liste des Roadbooks pr&eacute;sents :</h3>
(Cliquez sur un roadbook pour passer en mode annotation)
<form action="rm_rb.py" method="post">
<table>
""")

for fileitem in files:
  print ('<tr><td><input type="checkbox" name="choix" value="{}"></td><td><a href="annotation.py?fn={}"> {} </a></td>'.format(fileitem,fileitem,fileitem))

print ("""
</table>
<a href="upload.py"> <input type="button" value="Ajouter un roadbook"></a>
<a href="rm_rb.py" onclick="return confirm('Etes-vous s&ucirc;r de vouloir supprimer ?');"><input type="submit" value="Supprimer les roadbooks s&eacute;lectionn&eacute;s"></a>
</form>

<hr>
<a href="screen_setup.py"> <input type="button" value="Personnaliser les &eacute;crans"></a>
<a href="setup.py"> <input type="button" value="Configuration"></a>
</div>
</body>
</html>""")
