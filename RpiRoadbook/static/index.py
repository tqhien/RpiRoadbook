#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re

files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files.sort()

print ('Content-Type: text/html\n')
print ("<html>")
print ("<body>")
print ("""<h1>Gestionnaire du RpiRoadbook
<hr>
<h3>Liste des Roadbooks pr&eacute;sents :</h3>
(Cliquez sur un roadbook pour passer en mode annotation)
<form action="rm_rb.py" method="post">
""")

for fileitem in files:
  print ('<p><input type="checkbox" name="choix" value="{}"><a href="{}"> {} </a></p>'.format(fileitem,fileitem,fileitem))

print ("""
<input type="submit" value="Supprimer les s&eacute;lectionn&eacute;s">
</form>

<p></p>
<p></p>
<a href="upload.html"> <input type="button" value="Ajouter des roadbooks"></a>
<a href="setup.py"> <input type="button" value="Configuration"></a>
<a href="screen_setup.py"> <input type="button" value="Config. Affichages"></a>
</body>
</html>""")
