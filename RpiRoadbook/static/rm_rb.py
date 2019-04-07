#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import shutil

print ("""Content-Type: text/html\n
<html>
<head>
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Suppression de roadbooks</h1>
<hr>
""")

form = cgi.FieldStorage()

if 'choix' in form:
  # On recupere les noms de fichiers
  filefield = form['choix']
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
    print("<p>Suppression de {}</p>".format(fileitem.value))
else:
    print ("Pas de choix")
print ("""
<hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l'accueil"></a>
</div>
</body>
</html>""")
