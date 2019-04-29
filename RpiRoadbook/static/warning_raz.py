#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

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
  <h1>Configuration usine</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-blue w3-center">
   <h3>Le retour &agrave; la configuration usine effacera vos personnalisations</h3>
   <h3>(Param&egrave;tres et personalisation d'&eacute;crans)</h3>
   <h3>Les roadbooks et leurs annotations sont cependant gard&eacute;s !</h3>
   <h3>Etes-vous s&ucirc;r de vouloir continuer ?</h3>
    <div class="w3-bar w3-margin">
      <a class="w3-bar-item w3-button w3-black w3-hover-blue w3-margin-right" href="index.py">Annuler et revenir &agrave; l'accueil</a>
      <a class="w3-bar-item w3-button w3-red w3-hover-orange w3-margin-left" href="raz.py" onclick="return confirm('Etes-vous s&ucirc;r ?');">Continuer</a>
    </div>
</div>
<!-- Pied de page -->
<div class="w3-bar w3-black w3-margin">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>

</body>
</html>
""")
