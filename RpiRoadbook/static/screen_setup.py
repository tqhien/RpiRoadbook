#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi, os
import cgitb; cgitb.enable()
import configparser
import time

# Pour l'internationalisation
import gettext
_ = gettext.gettext

nb_screens = 4

screenconfig = configparser.ConfigParser()
setupconfig = configparser.ConfigParser()

# On charge les reglages : mode, orientation, etc
candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/setup.cfg','/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
setupconfig.read(candidates)

candidates = ['/home/hien/Developpement/RpiRoadbook/RpiRoadbook/screen.cfg','/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/screen.cfg']
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
  	<meta name="viewport" content="width=device-width, initial-scale=1">
  	<link rel="stylesheet" href="w3.css">
  	<link rel="stylesheet" href="font-awesome.min.css">
  	<link rel="stylesheet" href="material-icons.css">
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
  <!-- Entete -->
  <div class="w3-container w3-center w3-section">
  <h1>""")
print(_('Personnalisation des &eacute;crans'))
print("""</h1>
  </div>
<div class="w3-container">
<h3>""")
print(_('Choisissez un &eacute;cran &agrave; personnaliser'))
print("""</h3>
    <form action="save_screen.py" method="post">
        <div class="w3-row w3-black">
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran1');">
          <div class="w3-quarter tablink w3-hover-grey w3-padding w3-grey">""")
print(_('Ecran 1'))
print("""</div>
        </a>
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran2');">
          <div class="w3-quarter tablink w3-hover-light-blue w3-padding">""")
print(_('Ecran 2'))
print("""</div>
        </a>
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran3');">
          <div class="w3-quarter tablink w3-hover-light-green w3-padding">""")
print(_('Ecran 3'))
print("""</div>
        </a>
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran4');">
          <div class="w3-quarter tablink w3-hover-yellow w3-padding">""")
print(_('Ecran 4'))
print("""</div>
        </a>
        </div>
""")

for j in range (1,nb_screens+1):
    if j == 1 :
        print('<div id="Ecran{}" class="w3-row-padding screen w3-grey" style="display:block">'.format(j))
        print('<div class="w3-col m3">')
    elif j == 2 :
        print('<div id="Ecran{}" class="w3-row-padding screen w3-light-blue" style="display:none">'.format(j))
        print('<div class="w3-col m3"><br></div><div class="w3-col m3">')
    elif j == 3 :
        print('<div id="Ecran{}" class="w3-row-padding screen w3-light-green" style="display:none">'.format(j))
        print('<div class="w3-col m6"><br></div><div class="w3-col m3">')
    else :
        print('<div id="Ecran{}" class="w3-row-padding screen w3-yellow " style="display:none">'.format(j))
        print('<div class="w3-col m9"><br></div><div class="w3-col m3">')
    # Affichage des previews
    print('<img src="images/pajra1.png" id="preview_img{}">'.format(j))
    print('<table>')

    print('<tr><td>Jour/Nuit</td>')

    # Affichage des listes de choix jour_nuit
    print('<td>')
    print('<select name="jour_nuit{}" id="jour_nuit{}" onchange="update_preview()" style="width:110px;">'.format(j,j))
    print('<option value="Jour" selected="Jour">Jour</option>' if screenconfig['Affichage{}'.format(j)]['jour_nuit'] == 'Jour' else '<option value="Jour">Jour</option>')
    print('<option value="Nuit" selected="Nuit">Nuit</option>' if screenconfig['Affichage{}'.format(j)]['jour_nuit'] == 'Nuit' else '<option value="Nuit">Nuit</option>')
    print('</select>')
    print('</td>')
    print('</tr>')

# Affichage des listes de layout
    print('<tr><td>Disposition</td>')
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
        print('<option selected="Heure" value="Heure">Heure</option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Heure' else '<option value="Heure">Heure</option>')
        print('</select>')
        print('</td>')
        print('</tr>')
    print('</table></div>')
    print('</div>')

print("""

        <div class="w3-bar">
                <button class="w3-submit w3-btn w3-red w3-hover-teal w3-margin" type="submit">Valider</button>
        </div>
    </form>
    </div>

    <!-- Pied de page -->
    <div class="w3-bar w3-black">
      <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
      <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>Configuration</a>
    </div>

    <script>
function openScreen(evt, screenName) {
  var i, x, tablinks;
  x = document.getElementsByClassName("screen");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < x.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" w3-grey", "");
    tablinks[i].className = tablinks[i].className.replace(" w3-light-blue", "");
    tablinks[i].className = tablinks[i].className.replace(" w3-light-green", "");
    tablinks[i].className = tablinks[i].className.replace(" w3-yellow", "");
  }
  document.getElementById(screenName).style.display = "block";
  switch (screenName) {
    case 'Ecran1' :  evt.currentTarget.firstElementChild.className += " w3-grey"; break ;
    case 'Ecran2' :  evt.currentTarget.firstElementChild.className += " w3-light-blue"; break ;
    case 'Ecran3' :  evt.currentTarget.firstElementChild.className += " w3-light-green"; break ;
    case 'Ecran4' :  evt.currentTarget.firstElementChild.className += " w3-yellow"; break ;
  }
}
</script>
  </body>
</html>
""")
