#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import configparser

screenconfig = configparser.ConfigParser()

# On charge les reglages :
candidates = ['/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/RpiRoadbook_screen.cfg']
screenconfig.read(candidates)

print("""
Content-Type: text/html
<html>
<body>
""")

for i in range (1,6) :
    for j in range (1,4) :
        fji = 'f{}{}'.format(j,i)
        if fji in form:
            screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] = form[fij].value

for attempt in range(5):
  try :
    with open('/mnt/piusb/.conf/RpiRoadbook_screen.cfg', 'w') as configfile:
      screenconfig.write(configfile)
  except :
    subprocess.Popen('sudo mount -a',shell=True)
    time.sleep(.2)
  else :
    break
else :
  print('Write Error RpiRoadbook_screen.cfg after 5 tries')

print ("""
<a href="index.py"> <input type="button" value="Accueil"> </a>
</body></html>""")
