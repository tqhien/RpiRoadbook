#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

print("""
<html>
<head>
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
<div id="main">
<h1>Ajout d'un roadbook</h1>
<hr>
   <form enctype = "multipart/form-data"
                     action = "save_file.py" method = "post">
   <h3>S&eacute;lectionnez un fichier &agrave; t&eacute;l&eacute;charger : </h3>
   <input type = "file" name = "filename" />
   <br><input type = "submit" value = "Upload" />
   </form>
   <hr>
   <a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
</div>
</body>
</html>
""")
