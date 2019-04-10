#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re
import configparser

setupconfig = configparser.ConfigParser()
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/RpiRoadbook.cfg','/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
setupconfig.read(candidates)

print ('Content-Type: text/html\n')
print ("""<html>
<head>
<meta name="viewport" content="initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no">
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Changement de mode</h1>
<hr>
""")

setupconfig['Mode']['mode'] = 'Rallye'

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/RpiRoadbook.cfg', 'w') as configfile:
      setupconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    print ('Nouveau mode : Rallye')
    break
else :
  print('Write Error RpiRoadbook.cfg after 5 tries')

print("""
<hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
</div>
</body>
</html>""")
