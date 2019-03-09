#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser

screenconfig = configparser.ConfigParser()

# On charge les reglages : 
candidates = ['/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/RpiRoadbook_screen.cfg']
screenconfig.read(candidates)

print("""
<html>
<body>
   <form action = "save_screen.py" method = "post">

<table>
    <tr>
        <td></td>
        <td>Affichage 1</td>
        <td>Affichage 2</td>
        <td>Affichage 3</td>
    </tr>
    <tr>""")

for i in range (1,6) :
    print('<tr>')
    print('<td>Ligne {} : </td>'.format(i))
    for j in range (1,4) :
        print('<td>')
        print('<select id="f{}{}" name="f{}{}">'.format(j,i,j,i))
        print('<option selected=""></option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == '' else '<option></option>')
        print('<option selected="Heure">Heure</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Heure' else '<option>Heure</option>')
        print('<option selected="Chrono">Chrono</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Chrono' else '<option>Chrono</option>')
        print('<option selected="Decompte">Decompte</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Decompte' else '<option>Decompte</option>')
        print('<option selected="Vitesse">Vitesse</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vitesse' else '<option>Vitesse</option>')
        print('<option selected="Moyenne">Moyenne</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Moyenne' else '<option>Moyenne</option>')
        print('<option selected="Vmax">Vmax</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmax' else '<option>Vmax</option>')
        print('<option selected="Totalisateur">Totalisateur</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Totalisateur' else '<option>Totalisateur</option>')
        print('<option selected="Trip1">Trip1</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Trip1' else '<option>Trip1</option>')
        print('<option selected="Trip2">Trip2</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Trip2' else '<option>Trip2</option>')
        print('</select>')
        print('</td>')
    print('</tr>')
print('</table>')
print("""
    <input type = "submit" value = "Valider" />
   </form>
<a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
</body>
</html>""")
