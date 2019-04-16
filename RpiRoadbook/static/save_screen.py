#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import configparser

nb_screens = 4

screenconfig = configparser.ConfigParser()

# On charge les reglages :
candidates = ['/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/screen.cfg']
screenconfig.read(candidates)

print("Content-Type: text/html")
print("""
<html>
<head>
  <link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Configuration des &eacutecrans</h1>
<hr>
""")
for k in range (1,nb_screens+1) :
    jour_nuit = 'jour_nuit{}'.format(k)
    if jour_nuit in form:
        screenconfig['Affichage{}'.format(k)]['jour_nuit'] = form[jour_nuit].value
    luminosite = 'luminosite{}'.format(k)
    if luminosite in form:
        v = int(form[luminosite].value)
        if v > 100 :
            v = 100
        if v < 5 :
            v = 5
        screenconfig['Affichage{}'.format(k)]['luminosite'] = '{}'.format(v)
    layout = 'layout{}'.format(k)
    if layout in form:
        screenconfig['Affichage{}'.format(k)]['layout'] = form[layout].value
    for j in range (1,7) :
        champkj = 'champ{}{}'.format(k,j)
        if champkj in form:
            screenconfig['Affichage{}'.format(k)]['ligne{}'.format(j)] = form[champkj].value

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/screen.cfg', 'w') as configfile:
      screenconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    print('<h3>Configuration sauvegard&eacute; !</h3>')
    break
else :
  print('<h3>Write Error screen.cfg after 5 tries</h3>')

print ("""
<hr>
<a href="index.py"> <input type="button" value="Accueil"> </a>
</div></body></html>""")
