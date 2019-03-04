#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

if 'filenames' in form:
  # On recupere les noms de fichiers
  filefield = form['filenames']
  # un ou plusieurs noms de fichiers ?
  if not isinstance(filefield, list):
      filefield = [filefield]
  print ('Content-Type: text/html\n')
  print ("<html>")
  print ("<body>")
  for fileitem in filefield:
    # Test si le fichier a bien ete telecharge
    if fileitem.filename:
       # On ne garde que le nom du fichier
       # pour eviter des attaques par navigation dans l'arborescence
       fn = os.path.basename(fileitem.filename)
       open('/mnt/piusb/' + fn, 'wb').write(fileitem.file.read())
       message = 'Le fichier "' + fn + '" a bien &eacute;t&eacute; t&eacutel&eacute;charg&eacute'
    else:
       message = 'Aucun fichier telecharge'
    print ("<p>{}</p>".format(message))
    
  print ("<p></p>")
  print ('<a href="index.py"> <input type="button" value="Accueil"> </a>')
  print ("<p></p>")
  print ('<a href="upload.html"> <input type="button" value="T&eacute;l&eacute;charger d\'autres fichiers"></a>')
  print ("</body>")
  print ("</html>")