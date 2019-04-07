#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

if 'filename' in form:
  # On recupere le nom de fichier
  fileitem = form['filename']

  print ('Content-Type: text/html\n')
  print ("""<html>
  <head>
  <link rel="stylesheet" type="text/css" href="mystyle.css">
  </head>
  <body>
  <div id="main">
  <h1>Ajout de roadbooks</h1>
  <hr>""")
  # Test si le fichier a bien ete telecharge
  if fileitem.filename:
    # On ne garde que le nom du fichier
    # pour eviter des attaques par navigation dans l'arborescence
    fn = os.path.basename(fileitem.filename)
    open('/mnt/piusb/' + fn, 'wb').write(fileitem.file.read())
    message = 'Le fichier "' + fn + '" a bien &eacute;t&eacute; t&eacutel&eacute;charg&eacute'
  else:
    message = 'Aucun fichier telecharge'
  print ("<h3>{}</h3>".format(message))

  print ("""
<a href="upload.py"> <input type="button" value="T&eacute;l&eacute;charger d\'autres fichiers"></a>
<hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l'accueil"></a>
</div>
</body>
</html>
""")
