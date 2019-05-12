#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

import time

# Pour l'internationalisation
import gettext
_ = gettext.gettext

datetime_now = time.localtime ()
st_date = '{}-{:02d}-{:02d}'.format(datetime_now.tm_year,datetime_now.tm_mon,datetime_now.tm_mday)
st_time = '{:02d}:{:02d}'.format(datetime_now.tm_hour,datetime_now.tm_min)

print("""
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
</div>
<h1>
""")
print(_("R&eacute;glage de l'horloge"))
print("""
</h1>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-grey">
<form action = "save_clock.py" method = "post">
   <div class="w3-row-padding">
""")
print('   <div class="w3-half">')
print('    <label for="date"><h3>')
print(_('Date:'))
print('</h3></label>')
print('    <input type="date" id="date" name="user_date" value={}'.format(st_date))
print(' pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}">')
print('  </div>')

print('   <div class="w3-half">')
print('    <label for="time"><h3>')
print(_('Heure:'))
print('</h3></label>')
print('    <input type="time" id="time" name="user_time" value={}'.format(st_time))
print(' pattern="[0-9]{2}:[0-9]{2}">')
print('  </div>')

print("""
</div>
<div class="w3-bar">
        <button class="w3-submit w3-btn w3-red w3-hover-teal w3-margin" type="submit">
""")
print(_('Valider'))
print("""
</button>
</div>
   </form>
</div>

<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
  <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>
""")
print(_('Configuration'))
print("""
 </a>
</div>

</body>
</html>
""")
