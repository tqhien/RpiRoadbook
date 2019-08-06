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

fr = gettext.translation('static', localedir='locales', languages=['fr'])
en = gettext.translation('static', localedir='locales', languages=['en'])
it = gettext.translation('static', localedir='locales', languages=['it'])
de = gettext.translation('static', localedir='locales', languages=['de'])
es = gettext.translation('static', localedir='locales', languages=['es'])
langue = setupconfig['Parametres']['langue']
if langue == 'FR' :
    fr.install()
    _ = fr.gettext # Francais
elif langue == 'EN' :
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
print(_("Screen settings"))
print("""</h1>
  </div>
<div class="w3-container">
<h3>""")
print(_("Choose a screen to setup"))
print("""</h3>
    <form action="save_screen.py" method="post">
        <div class="w3-row w3-black">
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran1');">
          <div class="w3-quarter tablink w3-hover-grey w3-padding w3-grey">""")
print(_("Screen 1"))
print("""</div>
        </a>
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran2');">
          <div class="w3-quarter tablink w3-hover-light-blue w3-padding">""")
print(_("Screen 2"))
print("""</div>
        </a>
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran3');">
          <div class="w3-quarter tablink w3-hover-light-green w3-padding">""")
print(_("Screen 3"))
print("""</div>
        </a>
        <a href="javascript:void(0)" onclick="openScreen(event, 'Ecran4');">
          <div class="w3-quarter tablink w3-hover-yellow w3-padding">""")
print(_("Screen 4"))
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

    print('<tr><td>',_("Day/Night"),'</td>')

    # Affichage des listes de choix jour_nuit
    print('<td>')
    print('<select name="jour_nuit{}" id="jour_nuit{}" onchange="update_preview()" style="width:110px;">'.format(j,j))
    if screenconfig['Affichage{}'.format(j)]['jour_nuit'] == 'Jour' :
        print('<option value="Jour" selected="Jour">',_("Day"),'</option>')
    else :
        print('<option value="Jour">',_("Day"),'</option>')
    if screenconfig['Affichage{}'.format(j)]['jour_nuit'] == 'Nuit' :
        print('<option value="Nuit" selected="Nuit">',_("Night"),'</option>')
    else :
        print('<option value="Nuit">',_("Night"),'</option>')
    print('</select>')
    print('</td>')
    print('</tr>')

# Affichage des listes de layout
    print('<tr><td>',_("Layout"),'</td>')
    print('<td>')
    print('<select name="layout{}" id="layout{}" onchange="update_preview()" style="width:110px;">'.format(j,j))
    if orientation == 'Paysage' :
        if screenconfig['Affichage{}'.format(j)]['layout'] == '1' :
            print('<option selected="1" value="1">',_("3 Lines"),'</option>')
        else :
            print('<option value="1">',_("3 Lines"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['layout'] == '2' :
            print('<option selected="2" value="2">',_("4 Lines"),'</option>')
        else :
            print('<option value="2">',_("4 Lines"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['layout'] == '3' :
            print('<option selected="3" value="3">',_("5 Lines"),'</option>')
        else :
            print('<option value="3">',_("5 Lines"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['layout'] == '4' :
            print('<option selected="4" value="4">',_("6 Lines"),'</option>')
        else :
            print('<option value="4">',_("6 Lines"),'</option>')
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
        print('<option selected="Aucun" value="Aucun"></option>' if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == '' else '<option value="Aucun"></option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Totalisateur' :
            print('<option selected="Totalisateur" value="Totalisateur">',_("Distance"),'</option>')
        else :
            print('<option value="Totalisateur">',_("Distance"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Trip1' :
            print('<option selected="Trip1" value="Trip1">',_("Trip1"),'</option>')
        else :
            print('<option value="Trip1">',_("Trip1"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Trip2' :
            print('<option selected="Trip2" value="Trip2">',_("Trip2"),'</option>')
        else :
            print('<option value="Trip2">',_("Trip2"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vitesse' :
            print('<option selected="Vitesse" value="Vitesse">',_("Speed"),'</option>')
        else :
            print('<option value="Vitesse">',_("Speed"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmoy1' :
            print('<option selected="Vmoy1" value="Vmoy1">',_("Avg.Speed1"),'</option>')
        else :
            print('<option value="Vmoy1">',_("Avg.Speed1"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmoy2' :
            print('<option selected="Vmoy2" value="Vmoy2">',_("Avg.Speed2"),'</option>')
        else :
            print('<option value="Vmoy2">',_("Avg.Speed2"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Chrono1' :
            print('<option selected="Chrono1" value="Chrono1">',_("StopWatch1"),'</option>')
        else :
            print('<option value="Chrono1">',_("StopWatch1"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Chrono2' :
            print('<option selected="Chrono2" value="Chrono2">',_("StopWatch2"),'</option>')
        else :
            print('<option value="Chrono2">',_("StopWatch2"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Decompte' :
            print('<option selected="Decompte" value="Decompte">',_("Countdown"),'</option>')
        else :
            print('<option value="Decompte">',_("Countdown"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmax1' :
            print('<option selected="Vmax1" value="Vmax1">',_("Max.Speed1"),'</option>')
        else :
            print('<option value="Vmax1">',_("Max.Speed1"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Vmax2' :
            print('<option selected="Vmax2" value="Vmax2">',_("Max.Speed2"),'</option>')
        else :
            print('<option value="Vmax2">',_("Max.Speed2"),'</option>')
        if screenconfig['Affichage{}'.format(j)]['ligne{}'.format(i)] == 'Heure' :
            print('<option selected="Heure" value="Heure">',_("Time"),'</option>')
        else :
            print('<option value="Heure">',_("Time"),'</option>')
        print('</select>')
        print('</td>')
        print('</tr>')
    print('</table></div>')
    print('</div>')

print("""

        <div class="w3-bar">
                <button class="w3-submit w3-btn w3-red w3-hover-teal w3-margin" type="submit">""")
print(_("OK"))
print("""</button>
        </div>
    </form>
    </div>

    <!-- Pied de page -->
    <div class="w3-bar w3-black">
      <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
      <a href="setup.py" class="w3-bar-item w3-button w3-hover-blue w3-right"><i class="w3-xlarge fa fa-wrench"></i>""")
print(_("Setup"))
print("""</a>
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
