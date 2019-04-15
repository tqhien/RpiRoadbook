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
<h1>Retour &agrave la configuration d'usine</h1>
<hr>
""")

filelist = [
    '.conf/RpiRoadbook.cfg',
    '.conf/RpiRoadbook_setup.cfg',
    '.conf/RpiRoadbook_screen.cfg',
    '.conf/route.cfg',
    '.conf/screen.cfg',
    '.log/chrono.cfg',
    '.log/odo.cfg',
]

for fileitem in filelist:
    try:
        os.remove("/mnt/piusb/{}".format(fileitem))
    except :
        pass
    else:
        print('Suppression de {}'.format(fileitem))
print ("""
<hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l'accueil"></a>
</div>
</body>
</html>""")
