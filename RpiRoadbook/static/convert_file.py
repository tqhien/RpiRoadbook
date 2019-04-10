#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()

form = cgi.FieldStorage()

# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import page_count,convert_from_path,page_size
import subprocess

print ('Content-Type: text/html\n')
print ("""<html>
<head>
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>
  <script src="jquery-3.3.0.min.js"></script>

<div id="main">
<h1>Conversion</h1>
<hr>
<h3>Traitement en cours. Veuillez patienter</h3>
<div id="result"></div>
<script>
""")

if 'fn' in form:
  filename = form['fn'].value

if 'nb_colonnes' in form:
  nb_colonnes = int(form['nb_colonnes'].value)

if 'nb_lignes' in form:
  nb_lignes = int(form['nb_lignes'].value)

if 'margin_up' in form:
  marge_up = int(form['margin_up'].value)/297*1754

if 'margin_down' in form:
  marge_down = int(form['margin_down'].value)/297*1754

if 'lecture' in form:
  lecture = form['lecture'].value == 'rb'
else :
    lecture = False

filedir = os.path.splitext(filename)[0]
if os.path.isdir('/mnt/piusb/Conversions/'+filedir) == False: # Pas de répertoire d'images, on cree le repertoire
    os.mkdir('/mnt/piusb/Conversions/'+filedir)

# on vérifie le format de la page :
width, height = page_size ('/mnt/piusb/'+filename)
# conversion et découpage des cases
nb_pages = page_count ('/mnt/piusb/'+filename)
hauteur = (height/72*150-marge_up-marge_down)/nb_lignes ;
#Largeur d'une case (mm)
largeur = width/72*150/nb_colonnes
#Nombre de case par page
nb_cases = nb_lignes * nb_colonnes
total = nb_pages * nb_cases

w = round(largeur)
h = round(hauteur)

# on injecte dans la page html
print('var nb_colonnes = {};'.format(nb_colonnes))
print('var nb_lignes = {} ;'.format(nb_lignes))
print('var marge_up = {};'.format(marge_up))
print('var lecture = true ;' if lecture else 'var lecture = false ;')

print('var nb_pages = {} ;'.format(nb_pages))

print('var hauteur = {} ;'.format(hauteur))

print('var largeur = {} ;'.format(largeur))

print('var nb_cases = {};'.format(nb_cases))
print('var total = {} ;'.format(total))

print('var w = {};'.format(w))
print('var h = {};'.format(h))


print ("""

var i,j,k;

for (i=0;i<nb_pages;i++) {
    for (k=0;k<nb_colonnes;k++) {
        for (j=0;j<nb_lignes;j++) {
            x = Math.round(largeur*k)
            if (lecture) {
                y = Math.round(marge_up+(nb_lignes-j-1)*hauteur) }
            else {
                y = Math.round(marge_up+j*hauteur) }

            $.ajax({
              url: "convert_case.py",
                data: {
                  fn: 'test.pdf',
                  page:i,
                  x : x,
                  y:y,
                  w:w,
                  h:h,
                  num:i*nb_cases+k*nb_lignes+j,
                  total:total
                },
              success: function( result ) {
                  $( "#pdf_result" ).append( "Conversion <strong>" + result + "</strong> fait<br>" );
                }
            });
        }
    }
}
$( "#result" ).html( "<a href='index.py'> <input type='button' value='Accueil'> </a>" );

    </script>
<div id="pdf_result">
  </div>

<hr>
<a href="index.py"> <input type="button" value="Accueil"> </a>
</div>
</body>
</html>
""")
