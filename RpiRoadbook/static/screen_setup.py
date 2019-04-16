#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time

nb_screens = 4

screenconfig = configparser.ConfigParser()
setupconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

candidates = ['/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/screen.cfg']
screenconfig.read(candidates)

orientation = setupconfig['Parametres']['orientation']
if orientation == 'Paysage' :
    st = 'pa'
    nb_lignes = [3,4,5,6,3,3]
else:
    st = 'po'
    nb_lignes = [2,3,4,1,2,3]

print("""
<html>
  <head>
    <link rel="stylesheet" type="text/css" href="mystyle.css">
    <script type="text/javascript">
     function update_preview()
        {
        var st = ['','','','']; """)
print('var nb_lignes = {};'.format(nb_lignes))
print('for (k=1;k<{};k++)'.format(nb_screens+1),' {')
print("            st[k]='{}' ;".format(st))
print("""            var b = document.getElementById("jour_nuit"+k)[document.getElementById("jour_nuit"+k).selectedIndex].value
            switch (b)
            {
            case "Jour":
                st[k] = st[k] + 'j';
                break;
            case "Nuit":
                st[k] = st[k] + 'n';
                break;
            }

            st[k] = st[k] + 'ra';

            var d = document.getElementById("layout"+k)[document.getElementById("layout"+k).selectedIndex].value
            st[k] = st[k] + d

            //document.getElementById("preview").innerHTML = '<h1>'+st+'</h1>';
          	document.getElementById("preview_img"+k).src = 'images/'+st[k] + '.png';
          var j = document.getElementById("layout"+k).selectedIndex;
          var nb_l = nb_lignes[j]
          var i;
          for (i = 1;i<=nb_l;i++){
          	document.getElementById("champ"+k+i).style.display = "inline"
            document.getElementById("champ"+k+i).disabled = false;
          };
          for (i = nb_l+1;i<7;i++){
          	document.getElementById("champ"+k+i).style.display = "none";
            document.getElementById("champ"+k+i).disabled = true;
          }
          }


            //change_mode(listindex)

            return true;
        }

</script> </head>
  <body onload=update_preview()>
  <div id="main">
    <h1>Configuration des &eacutecrans</h1>
    <hr>
    <form action="save_screen.py" method="post">
        <table>
        <tr><th></th><th>Ecran 1</th><th>Ecran 2</th><th>Ecran 3</th><th>Ecran 4</th></tr>
""")
print('<tr><td>Preview</td>')
for j in range (1,nb_screens+1):
    # Affichage des previews
    print('<td>')
    print('<img src="images/pajra1.png" id="preview_img{}">'.format(j))
    print('</td>')
print('</tr><tr></tr>')

# Affichage des listes de choix jour_nuit
print('<tr><td>Mode</td>')
for j in range (1,nb_screens+1):
    print('<td>')
    print('<select name="jour_nuit{}" id="jour_nuit{}" onchange="update_preview()" style="width:110px;">'.format(j,j))
    print('<option value="Jour" selected="Jour">Jour</option>' if screenconfig['Affichage{}'.format(j)]['jour_nuit'] == 'Jour' else '<option value="Jour">Jour</option>')
    print('<option value="Nuit" selected="Nuit">Nuit</option>' if screenconfig['Affichage{}'.format(j)]['jour_nuit'] == 'Nuit' else '<option value="Nuit">Nuit</option>')
    print('</select>')
    print('</td>')
print('</tr>')

# Affichage des listes de layout
print('<tr><td>Disposition</td>')
for j in range (1,nb_screens+1):

    print('<td>')
    print('<select name="layout{}" id="layout{}" onchange="update_preview()" style="width:110px;">'.format(j,j))
    if orientation == 'Paysage' :
        print('<option selected="1" value="1">3 Champs</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '1' else '<option value="1">3 Champs</option>')
        print('<option selected="2" value="2">4 Champs</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '2' else '<option value="2">4 Champs</option>')
        print('<option selected="3" value="3">5 Champs</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '3' else '<option value="3">5 Champs</option>')
        print('<option selected="4" value="4">6 Champs</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '4' else '<option value="4">6 Champs</option>')
    else :
        print('<option selected="1" value="1">Layout 1</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '1' else '<option value="1">Layout 1</option>')
        print('<option selected="2" value="2">Layout 2</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '2' else '<option value="2">Layout 2</option>')
        print('<option selected="3" value="3">Layout 3</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '3' else '<option value="3">Layout 3</option>')
        print('<option selected="4" value="4">Layout 4</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '4' else '<option value="4">Layout 4</option>')
        print('<option selected="5" value="5">Layout 5</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '5' else '<option value="5">Layout 5</option>')
        print('<option selected="6" value="6">Layout 6</option>' if screenconfig['Affichage{}'.format(j)]['layout'] == '6' else '<option value="6">Layout 6</option>')

    print('</select>')
    print('</td>')
print('</tr><tr></tr>')
for i in range (1,7) :
    print('<tr>')
    print('<td>Widget {} : </td>'.format(i))
    for j in range (1,nb_screens+1) :
        print('<td>')
        print('<select id="champ{}{}" name="champ{}{}" style="width:110px;">'.format(j,i,j,i))
        print('<option selected="" value=""></option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == '' else '<option value=""></option>')
        print('<option selected="Totalisateur" value="Totalisateur">Odom&egrave;tre</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Totalisateur' else '<option value="Totalisateur">Odom&egrave;tre</option>')
        print('<option selected="Trip1" value="Trip1">Trip1</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Trip1' else '<option value="Trip1">Trip1</option>')
        print('<option selected="Trip2" value="Trip2">Trip2</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Trip2' else '<option value="Trip2">Trip2</option>')
        print('<option selected="Vitesse" value="Vitesse">Vitesse</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vitesse' else '<option value="Vitesse">Vitesse</option>')
        print('<option selected="Vmoy1" value="Vmoy1">Moyenne1</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmoy1' else '<option value="Vmoy1">Moyenne1</option>')
        print('<option selected="Vmoy2" value="Vmoy2">Moyenne2</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmoy2' else '<option value="Vmoy2">Moyenne2</option>')
        print('<option selected="Chrono1" value="Chrono1">Chrono1</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Chrono1' else '<option value="Chrono1">Chrono1</option>')
        print('<option selected="Chrono2" value="Chrono2">Chrono2</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Chrono2' else '<option value="Chrono2">Chrono2</option>')
        print('<option selected="Decompte" value="Decompte">Decompte</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Decompte' else '<option value="Decompte">Decompte</option>')
        print('<option selected="Vmax1" value="Vmax1">Vmax1</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmax1' else '<option value="Vmax1">Vmax1</option>')
        print('<option selected="Vmax2" value="Vmax2">Vmax2</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmax2' else '<option value="Vmax2">Vmax2</option>')
        print('</select>')
        print('</td>')
    print('</tr>')
print("""
        </table>
        <hr> <input value="Valider" type="submit">
    </form>
    <hr>
    <a href="index.py"> <input type="button" value="Retour &agrave; l\'accueil"></a>
    </div>
  </body>
</html>
""")
