#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import shutil
# Pour l'internationalisation
import gettext
_ = gettext.gettext

print ('Content-Type: text/html')
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
print(_('Annulation'))
print("""</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey w3-margin">
<h3>""")
print(_('Annulation du t&eacute;l&eacute;chargement :'))
print('</h3>')


form = cgi.FieldStorage()

if 'fn' in form:
  # On recupere les noms de fichiers
  filefield = form['fn']
  if not isinstance(filefield, list):
    filefield = [filefield]
  for fileitem in filefield:
    filedir = os.path.splitext(fileitem.value)[0]
    try:
        os.remove("/mnt/piusb/{}".format(fileitem.value))
    except :
        pass

    try:
        shutil.rmtree("/mnt/piusb/Conversions/{}".format(filedir))
    except:
        pass
    try:
      shutil.rmtree("/mnt/piusb/Annotations/{}".format(filedir))
    except:
        pass
    print("{}<br>".format(fileitem.value))
else:
    print (_('Pas de choix'))
print ("""
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>
</body>
</html>""")
