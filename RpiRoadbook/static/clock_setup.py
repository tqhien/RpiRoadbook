#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

import time

datetime_now = time.localtime ()
st_date = '{}-{:02d}-{:02d}'.format(datetime_now.tm_year,datetime_now.tm_mon,datetime_now.tm_mday)
st_time = '{:02d}:{:02d}'.format(datetime_now.tm_hour,datetime_now.tm_min)


print("""<html>
<head>
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>R&eacute;glage de l'horloge</h1>
<hr>
<form action="save_clock.py" method="post">
<table>
""")
print('   <tr>')
print('    <td><label for="date"><h3>Date:</h3></label></td>')
print('    <td><input type="date" id="date" name="user_date" value={}'.format(st_date))
print ('pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"></td>')
print('  </tr>')

print('   <tr>')
print('    <td><label for="time"><h3>Heure:</h3></label></td>')
print('    <td><input type="time" id="time" name="user_time" value={}'.format(st_time))
print ('pattern="[0-9]{2}:[0-9]{2}"></td>')
print('  </tr>')

print("""
</table>
    <input type = "submit" value = "Valider" /></p>
   </form>
   <hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
</div>
</body>
</html>""")
