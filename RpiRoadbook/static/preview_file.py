#!/usr/bin/pytho
# -*- coding: latin-1 -*
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

import re

# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import page_count,convert_from_path,page_size
import subprocess

if 'filename' in form:
  # On recupere le nom de fichier
  fileitem = form['filename']

  print ('Content-Type: text/html\n')
  print ("""<html>
  <head>
  <link rel="stylesheet" type="text/css" href="mystyle.css">
  </head>
  <body onload=init()>
  <div id="main">
  <h1>Ajout de roadbooks</h1>
  <hr>""")
  # Test si le fichier a bien ete telecharge
  if fileitem.filename:
    # On ne garde que le nom du fichier
    # pour eviter des attaques par navigation dans l'arborescence
    fn = os.path.basename(fileitem.filename)
    fn = re.sub(r"[\s-]","_",fn)
    filedir = os.path.splitext(fn)[0]
    open('/mnt/piusb/' + fn, 'wb').write(fileitem.file.read())
    message = 'Le fichier "' + fn + '" a &eacute;t&eacute; t&eacutel&eacute;charg&eacute;'
  else:
    message = 'Aucun fichier telecharge'
  print ("<h3>{}</h3>".format(message))
  print('Apercu du fichier : \n')
  # Taille en Postcript point, soit en 72 dpi donc /72*2.54 pour avoir la taille en cm puis ou /72*150 pour avoir le nb de pixel si on extrait a 150dpi
  # pour une page A4, on a donc 595x842 pts, soit une image de 1240x1754px (595/72*150,842/72*150)
  width, height = page_size ('/mnt/piusb/'+fn)
  #print(width,height)
  page = convert_from_path('/mnt/piusb/'+fn, output_folder='/mnt/piusb/thumbnail/',first_page = 1, last_page=1, dpi=150, singlefile='{:03}'.format(0), fmt='jpg')
  print("""
  <div id="mycanvas" style="position:relative;height:425px">
  <div style="float:left;left:0;">
  <canvas id="imageView" width="300" height="425" style="position: absolute; top: 0; z-index: 0;"></canvas>
  <canvas id="annotation" width="300" height="425" style="position: absolute; top: 0;z-index: 1;"></canvas>
  </div>
  <div style="margin-left:300px">
  <form action = "convert_file.py" method = "post">
  """)
  print('<input type="hidden" name="fn" value="{}">'.format(fn))
  print("""<table>
        <tr><td>NB Colonnes</td><td><input type="number" name="nb_colonnes" id="nb_colonnes" value="2" onchange="init()" min="1" step="1" oninput="validity.valid||(value='');"></td></tr>
        <tr><td>NB Lignes par colonne</td><td><input type="number" name="nb_lignes" id="nb_lignes" value="8" onchange="init()" min="1" step="1" oninput="validity.valid||(value='');"></td></tr>
        <tr><td>Marge haute</td><td><input type="number" name="margin_up" id="margin_up" value="30" onchange="init()" min="1" step="1" oninput="validity.valid||(value='');">mm</td></tr>
        <tr><td>Marge basse</td><td><input type="number" name="margin_down" id="margin_down" value="27" onchange="init()" min="1" step="1" oninput="validity.valid||(value='');">mm</td></tr>
        <tr><td>Lecture de bas en haut</td><td><input type="checkbox" name="lecture" id="lecture" value="rb" checked onchange="init()"></td></tr>
  </table>
<input type="submit" value="Convertir"/>
</form>
<a href="cancel_file.py"> <input type="button" value="Annuler"></a>
  </div>

  </div>
<hr>
<h3><h3>Preview de la 1&egrave;re case
<div>
<canvas id="hiddenImg" width="1240" height="1754" style="display:none"></canvas>
</div>
<div>
<canvas id="previewImg" width="1240" height="480"></canvas>
</div>


  <script type="text/javascript">
  var layer1;
  var layer2;
  var layer3;
  var layer4;
  var ctx1;
  var ctx2;
  var ctx3;
  var ctx4;
  var base = new Image();
  var preview = new Image();

  function init() {
  """)
  print("base.src='thumbnail/{}_000.jpg';".format(filedir))
  print("""
    layer1 = document.getElementById("imageView");
    ctx1 = layer1.getContext("2d");
    ctx1.drawImage(base, 0, 0, 300,425);
    layer2 = document.getElementById("annotation");
    ctx2 = layer2.getContext("2d");
    layer3 = document.getElementById("hiddenImg");
    ctx3 = layer3.getContext("2d");
    ctx3.drawImage(base, 0, 0);
    layer4 = document.getElementById("previewImg");
    ctx4 = layer4.getContext("2d");
    var nb_colonnes = parseInt(document.getElementById("nb_colonnes").value) ;
    var nb_lignes = parseInt(document.getElementById("nb_lignes").value) ;
    var marge_up = parseInt(document.getElementById("margin_up").value) ;
    var marge_down = parseInt(document.getElementById("margin_down").value) ;
    var hauteur = (297-marge_up-marge_down)/nb_lignes ;
    var lecture = document.getElementById("lecture").checked ;
    ctx2.clearRect(0,0,layer2.width,layer2.height)
    ctx2.strokeStyle = "#FF0000";
    ctx2.font = "40px Arial";
    ctx2.fillStyle = "red";
    ctx2.textAlign = "center";
    var i;
    var y;
    for (i=1;i<=nb_lignes;i++) {
        if (lecture) {
            y = marge_up+(nb_lignes-i)*hauteur;
        } else {
            y = marge_up+(i-1)*hauteur;
        }
        ctx2.strokeRect(0, y/297*425, 300/nb_colonnes,hauteur/297*425);
        ctx2.fillText(i, 300/nb_colonnes/2, y/297*425+2*hauteur/297*425/3);
    }
    if (lecture) {
        y = marge_up+(nb_lignes-1)*hauteur;
    } else {
        y = marge_up;
    }
    //preview = ctx1.getImageData(0, marge_up/297*425, 300/nb_colonnes,hauteur/297*425);
    preview = ctx3.getImageData(0, y/297*1754, 1240/nb_colonnes,hauteur/297*1754);
    ctx4.clearRect(0,0,layer4.width,layer4.height)
    ctx4.putImageData(preview,0,0)
  }

  init();
  </script>
<hr>
<a href="index.py"> <input type="button" value="Retour &agrave; l'accueil"></a>
</div>
</body>
</html>
""")
