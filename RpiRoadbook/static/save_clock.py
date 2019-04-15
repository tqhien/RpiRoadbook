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
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>R&eacute;glage de l'horloge</h1>
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
<a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
</div>
</body>
</html>
""")
