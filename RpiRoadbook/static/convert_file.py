#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re
import math

import configparser
setupconfig = configparser.ConfigParser()
# Pour l'internationalisation
import gettext
_ = gettext.gettext
# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

en = gettext.translation('static', localedir='locales', languages=['en'])
it = gettext.translation('static', localedir='locales', languages=['it'])
de = gettext.translation('static', localedir='locales', languages=['de'])
es = gettext.translation('static', localedir='locales', languages=['es'])
langue = setupconfig['Parametres']['langue']
if langue == 'EN' :
    en.install()
    _ = en.gettext # English
elif langue == 'IT' :
    it.install()
    _ = it.gettext # Italiano
elif langue == 'DE' :
    de.install()
    _ = de.gettext
elif langue == 'ES' :
    es.install
    _ = es.gettext


form = cgi.FieldStorage()

# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import page_count,convert_from_path,page_size
import subprocess

print ('Content-Type: text/html\n')
print ("""<html>
 <head>
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <link rel="stylesheet" href="w3.css">
   <link rel="stylesheet" href="font-awesome.min.css">
   <link rel="stylesheet" href="material-icons.css">
 </head>
<body>
  <script src="jquery-3.3.0.min.js"></script>

<!-- Entete -->
<div class="w3-container w3-center w3-section">
<h1>""")
print(_('Conversion'))
print("""</h1>
</div>
<div class="w3-container w3-section w3-topbar w3-bottombar w3-border-red">
<div class="w3-row">
  <div class="w3-col w3-light-grey s12 w3-center">
<p><h3>""")
print(_('Traitement en cours. Veuillez patienter'))
print('</h3></p>')

print(_('La liste des cases appara&icirc;tra une fois la conversion termin&eacute;e (environ 1 seconde/case)'))
print("""
</div>
</div>
</div>
<script>
""")

if 'fn' in form:
  filename = form['fn'].value
  filename = re.sub(r"[\s-]","-",filename)

filedir = os.path.splitext(filename)[0]
if os.path.isdir('/mnt/piusb/Conversions/'+filedir) == False: # Pas de répertoire d'images, on cree le repertoire
    os.mkdir('/mnt/piusb/Conversions/'+filedir)

# on vérifie le format de la page :
width, height = page_size ('/mnt/piusb/'+filename)
width_px = math.floor(width/72*150)
height_px = math.floor(height/72*150)
width_mm = width/72*25.4
height_mm = height/72*25.4

if 'nb_colonnes' in form:
  nb_colonnes = int(form['nb_colonnes'].value)

if 'nb_lignes' in form:
  nb_lignes = int(form['nb_lignes'].value)

if 'margin_up' in form:
  marge_up = int(form['margin_up'].value)/height_mm*height_px

if 'margin_down' in form:
  marge_down = int(form['margin_down'].value)/height_mm*height_px

if 'lecture' in form:
  lecture = form['lecture'].value == 'rb'
else :
    lecture = False


# conversion et découpage des cases
nb_pages = page_count ('/mnt/piusb/'+filename)
#hauteur en pixels
hauteur = (height_px-marge_up-marge_down)/nb_lignes ;
#Largeur d'une case (en pixel)
largeur = width_px/nb_colonnes
#Nombre de case par page
nb_cases = nb_lignes * nb_colonnes
total = nb_pages * nb_cases

w = round(largeur)
h = round(hauteur)

# on injecte dans la page html
print('var filename = "{}"'.format(filename))
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

#num:i*nb_cases+k*nb_lignes+j,
#total:total

print ("""

$.ajax({
  url: "convert_case.py",
    data: {
      fn: filename,
      nb_pages:nb_pages,
      nb_colonnes:nb_colonnes,
      nb_lignes:nb_lignes,
      largeur:largeur,
      lecture:lecture,
      marge_up:marge_up,
      hauteur:hauteur,
      w:w,
      h:h,
      total:total
    },
  success: function( result ) {
      $( "#pdf_result" ).append( result + "<br>" );
    }
});

    </script>
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>
<div class="w3-container w3-center" id="pdf_result">
  </div>
</body>
</html>
""")
