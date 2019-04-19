#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time
import subprocess

form = cgi.FieldStorage()

st_date = ''
st_time = ''

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
<h1>R&eacute;glage de l'horloge</h1>
</div>
<hr>
<h3>R&eacute;glage sauvegard&eacute; :</h3>
""")

if 'user_date' in form:
  st_date = form['user_date'].value
  print ('{}\n'.format(st_date))

if 'user_time' in form:
  st_time = form['user_time'].value
  print ('{}\n'.format(st_time))

subprocess.Popen ('date "{} {}"'.format(st_date,st_time),shell=True)
subprocess.Popen ('hwclock --set --date "{} {}" --utc --noadjfile'.format(st_date,st_time),shell=True)
subprocess.Popen ('hwclock -w',shell=True)

print("""
<hr>
<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue">Configuration</a>
  <a href="screen_setup.py" class="w3-bar-item w3-button w3-hover-blue">Personnaliser les affichages</a>
  <a href="raz.py" class="w3-bar-item w3-button w3-right w3-hover-red">Config. Usine</a>
  <a href="ota.py" class="w3-bar-item w3-button w3-right w3-hover-red">MAJ Firmware</a>
</div>
</body>
</html>
""")
