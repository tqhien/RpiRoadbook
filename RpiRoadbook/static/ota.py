#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

# Pour l'internationalisation
import gettext
_ = gettext.gettext

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
  <h1>""")
print(_('Mise &agrave; jour Firmware'))
print("""</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-blue">
   <form enctype="multipart/form-data" action="save_ota.py" method = "post">
   <h3>""")
print(_('S&eacute;lectionnez le firmware &agrave; t&eacute;l&eacute;charger : '))
print("""</h3>
   <input class="w3-input w3-button " type="file" name="filename" />
   <input class="w3-input w3-teal w3-button w3-hover-blue w3-left-align w3-margin" type="submit" value=" """)
print(_('T&eacute;l&eacute;charger le firmware...'))
print(""" " />
   </form>
</div>
<!-- Pied de page -->
<div class="w3-bar w3-black w3-margin">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>

</body>
</html>
""")
