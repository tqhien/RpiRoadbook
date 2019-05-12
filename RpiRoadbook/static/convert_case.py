#!/usr/bin/python
import cgi, os
import cgitb; cgitb.enable()
import re

# Pour l'internationalisation
import gettext
_ = gettext.gettext

form = cgi.FieldStorage()

# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import convert_from_path
#import subprocess

#print ('Content-type: text/html')
#print("""
#print('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')
print('<html>')


if 'fn' in form:
   filename = form['fn'].value
   filename = re.sub(r"[\s-]","-",filename)
   filedir = os.path.splitext(filename)[0]
   #print(filename)

if 'nb_pages' in form:
    nb_pages = int(form['nb_pages'].value)
    #print(i)

if 'nb_colonnes' in form:
    nb_colonnes = int(form['nb_colonnes'].value)

if 'nb_lignes' in form:
    nb_lignes = int(form['nb_lignes'].value)

if 'largeur' in form:
    largeur = float(form['largeur'].value)

if 'lecture' in form:
    lecture = form['lecture'].value == 'true'

if 'marge_up' in form:
    marge_up = float(form['marge_up'].value)

if 'hauteur' in form:
    hauteur = float(form['hauteur'].value)

if 'w' in form:
    w = int(form['w'].value)

if 'h' in form:
    h = int(form['h'].value)

if 'total' in form:
    total = int(form['total'].value)

nb_cases = nb_lignes * nb_colonnes

for i in range (nb_pages) :
    for k in range(nb_colonnes):
        for j in range (nb_lignes) :
            x = round(largeur*k)
            if lecture :
                y = round(marge_up+(nb_lignes-j-1)*hauteur)
            else :
                y = round(marge_up+j*hauteur)
            num = i*nb_cases+k*nb_lignes+j
            pages = convert_from_path('/mnt/piusb/'+filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile='{:03}'.format(num),fmt='jpg')

            print(_('Case {} / {}<br>').format(num+1,total))

print ('</html>')
