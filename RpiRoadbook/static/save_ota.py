#!/usr/bin/python
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import re

import subprocess

print ('Content-Type: text/html\n')
print ("""
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
  <h1>Mise &agrave; jour de firmware</h1>
  </div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-red">
<div class="w3-row">
<div class="w3-col w3-light-grey s12 w3-center">
""")


if 'filename' in form:
  # On recupere le nom de fichier
  fileitem = form['filename']
  # Test si le fichier a bien ete telecharge
  if fileitem.filename:
    open('/mnt/piusb/ota/ota.tar.gz', 'wb').write(fileitem.file.read())
    print('<h3>Firmware t&eacute;l&eacute;charg&eacute;.</h3><br>')
    print('<h3>Attendez 5 secondes et red&eacute;marrez le RpiRoadbook</h3><br>')
    print('<h3>pour appliquer la mise &agrave; jour.</h3><br>')
print("""
</div>
</div>
</div>
  <!-- Pied de page -->
  <div class="w3-bar w3-black">
    <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  </div>
  </body>
  </html>
""")
