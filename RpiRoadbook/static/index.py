#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re

#files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files.sort()

print ('Content-Type: text/html\n')
print ("""<html>
<head>
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Gestionnaire du RpiRoadbook</h1>
<hr>
<h3>Liste des Roadbooks pr&eacute;sents :</h3>
(Cliquez sur un roadbook pour passer en mode annotation)
<form action="rm_rb.py" method="post">
<table>
""")

for fileitem in files:
  print ('<tr><td><input type="checkbox" name="choix" value="{}"></td><td><a href="rb_edit.py?rb={}"> {} </a></td>'.format(fileitem,fileitem,fileitem))

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
