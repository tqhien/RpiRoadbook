#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import base64
import re
from PIL import Image

import configparser
setupconfig = configparser.ConfigParser()
# Pour l'internationalisation
import gettext
_ = gettext.gettext
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


form = cgi.FieldStorage()
#print(form)

if 'fn' in form:
    filename = form['fn'].value
    filename = re.sub(r"[\s-]","-",filename)
    filedir = os.path.splitext(filename)[0]

if 'num' in form:
    num = int(form['num'].value)
else:
    num = 0


DIR = '/mnt/piusb/Conversions/{}'.format(filedir)
files = [f for f in os.listdir(DIR) if re.search('.jpg$', f)]
files.sort()
nmax = len(files)
img_name = os.path.join(DIR,files[num])
img = Image.open(img_name)
w,h = img.size
anum = os.path.splitext(files[num])[0]
anum = anum.replace(filedir,'')
anum = anum.replace('.jpg','')

print("""
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
   <link rel="stylesheet" href="w3.css">
   <link rel="stylesheet" href="font-awesome.min.css">
   <link rel="stylesheet" href="material-icons.css">
   <style>
   """)
print('       @media (max-width: {}px)'.format(w))
print("""
       {
         #ma_case,#canvasDiv {
         width: 90%;
         }

       }
   </style>

    <script type="text/javascript" src="fabric.min.js"></script>
    <script type="text/javascript" src="jquery-3.3.0.min.js"></script>
    <script>

    $(document).ready(function () {
          initialize();
       });

    function initialize() {
      $(function () {
         $("#save_canvas").click(function () {
           canvas.setBackgroundImage(null, canvas.renderAll.bind(canvas));
            var image = canvas.toDataURL("image/png");
            image = image.replace('data:image/png;base64,', '');
            $.ajax({
                type : 'POST',
                url: 'save_annotation.py',
                data: {
                  imagedata : image ,
""")
print('         fn : "{}",'.format(filename))
print('                  num : "{}"'.format(anum))
print("""
                },
                 success: function (result) {
                      $( "#canvas_result" ).append( result + "<br>" );
                 }
            });
            canvas.setBackgroundImage(img.src, canvas.renderAll.bind(canvas), {
                     originX: 'left',
                     originY: 'top',
                     left: 0,
                     top: 0
                 });
         });

         $("#add_case").click(function () {
            var canvas_add = document.getElementById("new_case")
            var image = canvas_add.toDataURL("image/png");
            image = image.replace('data:image/png;base64,', '');
            $.ajax({
                type : 'POST',
                url: 'add_case.py',
                data: {
                  imagedata : image ,
""")
print('         fn : "{}",'.format(filename))
print('         num : "{}"'.format(os.path.splitext(files[num])[0]))
print("""
                },
                 success: function (result) {
                      $( "#canvas_result" ).append( result + "<br>" );
                 }
            });
         });
      });
    };


      function rgb(r, g, b){
        return "rgb("+r+","+g+","+b+")";
      }

      function rgba(r, g, b,a){
        return "rgba("+r+","+g+","+b+","+a+")";
      }

      function setcolor(r,g,b) {
        current_color = rgb(r,g,b,0.5);
        current_alpha_color = rgba(r,g,b,alpha);
        canvas.freeDrawingBrush.color = rgb(r,g,b) ;
        if (canvas.getActiveObject()) {
          var e = canvas.getActiveObject() ;
          switch (e.get('type')) {
            case 'textbox' :
              canvas.getActiveObject().fill = current_color ;
              canvas.getActiveObject().stroke = current_color ;
              break ;
            case 'rect' :
              canvas.getActiveObject().fill = current_alpha_color ;
              break;
            case 'path' :
              canvas.getActiveObject().stroke = current_color ;
              break ;
          }
          canvas.getActiveObject().dirty = true ;
          canvas.renderAll() ;
        }
      };

      function setbgcolor(r,g,b,a) {
        current_bg_color = rgba(r,g,b,a);
        if (canvas.getActiveObject()) {
          var e = canvas.getActiveObject() ;
          if (e.get('type') === 'textbox') {
            canvas.getActiveObject().textBackgroundColor = current_bg_color ;
            canvas.getActiveObject().dirty = true ;
            canvas.renderAll() ;
          }
        }

      };

      function setNoMode()
      {
        canvas.off('mouse:down');
        canvas.off('mouse:move');
        canvas.isDrawingMode = false;
        var i, tablinks;
        tablinks = document.getElementsByClassName("toollink");
        for (i = 0; i < tablinks.length; i++) {
          tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
        } ;
        canvas.discardActiveObject();
        canvas.renderAll() ;
      };

      function setPencilMode()
      {
        canvas.discardActiveObject();
        canvas.renderAll() ;
        canvas.off('mouse:down');
        canvas.off('mouse:move');
        canvas.isDrawingMode = true;
        canvas.freeDrawingBrush.width = slider1.value;

        canvas.on('mouse:up', function(o){
          var i, tablinks;
          canvas.off('mouse:down');
          canvas.off('mouse:move');
          tablinks = document.getElementsByClassName("toollink");
          for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
          }
          canvas.isDrawingMode = false;
        });
      };

      function setRectMode()
      {
        canvas.discardActiveObject();
        canvas.renderAll() ;
        canvas.isDrawingMode = false;
        canvas.off('mouse:down');
        canvas.off('mouse:move');
        var rect, isDown, origX, origY;

        canvas.on('mouse:down', function(o){
            isDown = true;
            var pointer = canvas.getPointer(o.e);
            origX = pointer.x;
            origY = pointer.y;
            var pointer = canvas.getPointer(o.e);
            rect = new fabric.Rect({
                left: origX,
                top: origY,
                originX: 'left',
                originY: 'top',
                width: pointer.x-origX,
                height: pointer.y-origY,
                angle: 0,
                fill: current_alpha_color,
                transparentCorners: false,
                hasControls: true,
                selectable:true
            });
            canvas.add(rect);

        });

        canvas.on('mouse:move', function(o){
            if (!isDown) return;
            var pointer = canvas.getPointer(o.e);

            if(origX>pointer.x){
                rect.set({ left: Math.abs(pointer.x) });
            }
            if(origY>pointer.y){
                rect.set({ top: Math.abs(pointer.y) });
            }

            rect.set({ width: Math.abs(origX - pointer.x) });
            rect.set({ height: Math.abs(origY - pointer.y) });


            canvas.renderAll();
        });

        canvas.on('mouse:up', function(o){
          var i, tablinks;
          isDown = false;
          canvas.off('mouse:down');
          canvas.off('mouse:move');
          tablinks = document.getElementsByClassName("toollink");
          for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
          }
        });
      };

      function setTextMode()
      {
        canvas.discardActiveObject();
        canvas.renderAll() ;
        canvas.isDrawingMode = false;
        canvas.off('mouse:down');
        canvas.off('mouse:move');
        var textbox, isDown, origX, origY;

        canvas.on('mouse:down', function(o){
            isDown = true;
            var pointer = canvas.getPointer(o.e);
            origX = pointer.x;
            origY = pointer.y;
            textbox = new fabric.Textbox('Texte',{
                left: origX,
                top: origY,
                originX: 'left',
                originY: 'top',
                width: 150,
                height: 50,
                angle: 0,
                fill: current_color,
                strokeWidth: 2,
                stroke: current_color,
                textBackgroundColor: current_bg_color,
                fontSize: slider3.value,
                transparentCorners: false,
                lockScalingX: true,
                lockScalingY: true,
                lockRotation: true,
                hasControls: false
            });
            canvas.add(textbox);

        });

        canvas.on('mouse:up', function(o){
          var i, tablinks;
          isDown = false;
          canvas.off('mouse:down');
          canvas.off('mouse:move');
          tablinks = document.getElementsByClassName("toollink");
          for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
          }
        });



      };

      function gopage() {
        var mytext = document.getElementById("myPos") ;
        var jto = mytext.value;
        console.log(jto)
      };

      function openScreen(evt, toolName) {
        var i, x, tablinks;
        x = document.getElementsByClassName("tools");
        for (i = 0; i < x.length; i++) {
          x[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("toollink");
        for (i = 0; i < x.length; i++) {
          tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
        }
        document.getElementById(toolName).style.display = "block";
        evt.currentTarget.className += " w3-red";
        canvas.discardActiveObject();
      };

      function updateObject() {
        var e = canvas.getActiveObject() ;
        switch (e.get('type')) {
          case 'textbox' :
            slider3.value = e.fontSize ;
            output3.innerHTML = 'Taille Police : '+e.fontSize + ' px';
            var c = new fabric.Color(e.fill) ;
            current_color = c.getSource() ;
            current_bg_color = e.textBackgroundColor ;
            var i, x, tablinks;
            x = document.getElementsByClassName("tools");
            for (i = 0; i < x.length; i++) {
              x[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("toollink");
            for (i = 0; i < x.length; i++) {
              tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
            }
            document.getElementById('Text').style.display = "block";
            break ;
          case 'rect' :
            var c = new fabric.Color(e.fill) ;
            alpha = c.getAlpha() ;
            var b = c.getSource() ;
            current_alpha_color = c ;
            slider2.value = Math.round((1-alpha)*100) ;
            output2.innerHTML = 'Transparence : '+Math.round((1-alpha)*100) + ' %';
            var i, x, tablinks;
            x = document.getElementsByClassName("tools");
            for (i = 0; i < x.length; i++) {
              x[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("toollink");
            for (i = 0; i < x.length; i++) {
              tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
            }
            document.getElementById('Rectangle').style.display = "block";
            break ;
          case 'path' :
            slider1.value = e.strokeWidth ;
            output1.innerHTML = 'Epaisseur : '+e.strokeWidth+ ' px';
            canvas.freeDrawingBrush.width = e.strokeWidth;
            var i, x, tablinks;
            x = document.getElementsByClassName("tools");
            for (i = 0; i < x.length; i++) {
              x[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("toollink");
            for (i = 0; i < x.length; i++) {
              tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
            }
            document.getElementById('Pencil').style.display = "block";
            break ;
        }
      } ;

    </script>

  </head>

<body>
  <!-- Entete -->
  <div class="w3-container w3-center w3-section w3-hide-small">
     <h1>""")
print(_("Notes"))
print("""</h1>
  </div>

  <div class="w3-bar">
""")
print('<a href="text_editor.py?fn={}&num=0" class="w3-button"> <i class="w3-xlarge fa fa-fast-backward"></i> </a>'.format(filename) if num > 0 else '<a href="#" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-fast-backward"></i> </a>')
print('<a href="text_editor.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-backward"></i> </a>'.format(filename,num-10) if num-10>=0 else '<a href="#" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-backward"></i> </a>')
print('<a href="text_editor.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-chevron-left"></i> </a>'.format(filename,num-1) if num-1 >= 0 else '<a href="#" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-chevron-left"></i> </a>')
print('    <input type="text" id="myPos" value="{}"><input type="button" value="'.format(num+1),_("Goto..."),'" onClick="gopage()">')
print('<a href="text_editor.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-chevron-right"></i> </a>'.format(filename,num+1) if nmax > num+1 else '<a href="#" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-chevron-right"></i> </a>')
print('<a href="text_editor.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-forward"></i> </a>'.format(filename,num+10) if nmax > num+10 else '<a href="#" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-forward"></i> </a>')
print('<a href="text_editor.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-fast-forward"></i> </a>'.format(filename,nmax-1) if num <nmax-1 else '<a href="#" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-fast-forward"></i> </a>')
print("""
  </div>

  <div class="w3-bar w3-black">
    <button class="w3-bar-item w3-button toollink" onclick="setNoMode();"><i class="w3-xlarge fa fa-mouse-pointer"></i></button>
    <button class="w3-bar-item w3-button toollink" onclick="setPencilMode();openScreen(event, 'Pencil');"><i class="w3-xlarge fa fa-pencil"></i></button>
    <button class="w3-bar-item w3-button toollink" onclick="setRectMode();openScreen(event, 'Rectangle');"><i class="w3-xlarge fa fa-square"></i></button>
    <button class="w3-bar-item w3-button toollink" onclick="setTextMode();openScreen(event, 'Text');"><i class="w3-xlarge material-icons">text_fields</i></button>

  </div>
  <div class="w3-bar" id="Colorbar">
    <button class="w3-button w3-circle w3-red w3-border" onclick="setcolor(255,0,0);">R</button>
    <button class="w3-button w3-circle w3-border w3-green" onclick="setcolor(0,255,0);">V</button>
    <button class="w3-button w3-circle w3-border w3-blue " onclick="setcolor(0,0,255);">B</button>
    <button class="w3-button w3-circle w3-border w3-yellow" onclick="setcolor(255,255,0);">J</button>
    <button class="w3-button w3-circle w3-border w3-orange" onclick="setcolor(255,125,0);">O</button>
    <button class="w3-button w3-circle w3-border w3-black " onclick="setcolor(0,0,0);">N</button>
    <button class="w3-button w3-circle w3-border w3-white " onclick="setcolor(255,255,255);">W</button>
  </div>
  <div class="w3-bar tools" id="Pencil">
    <div class="w3-bar slidecontainer">
      <input type="range" min="1" max="20" value="5" class="slider" id="myWidth">
      <div id="demo1" class="w3-bar-item">""")
print(_("Width"))
print(' : 5 px</div>')
print("""
    </div>
  </div>
  <div class="w3-bar tools" id="Rectangle" style="display:none">
    <div class="w3-bar slidecontainer">
      <input type="range" min="0" max="100" value="50" class="slider" id="myAlpha">
      <div id="demo2" class="w3-bar-item">""")
print(_("Transparency"))
print(' : 50 %</div>')
print("""
    </div>
  </div>
  <div class="w3-bar tools" id="Text" style="display:none">
    <div class="w3-bar slidecontainer">
      <input type="range" min="6" max="100" value="30" class="slider" id="myPolice">
      <div id="demo3" class="w3-bar-item">""")
print(_("Font Size"))
print(' : 30 px</div>')
print(_("Background Color :"))
print('    <button class="w3-button w3-border w3-black Text" onclick="setbgcolor(0,0,0,1);">')
print(_("Black"))
print('</button>    <button class="w3-button w3-border w3-white Text" onclick="setbgcolor(255,255,255,1);">')
print(_("White"))
print('</button>    <button class="w3-button w3-border w3-light-grey Text" onclick="setbgcolor(255,255,255,0.5);">')
print(_("Transparent"))
print("""</button>
    </div>
  </div>
  """)
print('<div id="canvasDiv" style="position:relative;height:{}px;">'.format(h))

print('<canvas id="ma_case" width="{}px" height="{}px" style="position:absolute;top:0px;border:2px solid #000000;"></canvas>'.format(w,h))
print("""
</div>

<div class="w3-bar">
  <a href="#" class="w3-bar-item w3-button w3-red w3-hover-blue" id="save_canvas" name="save_canvas">""")
print(_("Save"))
print(' </a>  <a href="#" class="w3-bar-item w3-button w3-hover-blue" onclick="erase()" id="raz_canvas" name="raz_canvas"> ')
print(_("Clear Note"))
print('</a>  <a href="#" class="w3-bar-item w3-button" id="add_case"><i class="w3-xlarge fa fa-indent"></i> ')
print(_("Insert"))
print("""</a>
  <form action="rm_case.py" method="POST">
  """)
print('    <input type="text" id="fn" name="fn" value="{}" style="display:none">'.format(filename))
print('    <input type="text" id="num" name="num" value="{}" style="display:none">'.format(num))
print("""
  <button class="w3-bar-item w3-button" type="submit"><i class="w3-xlarge fa fa-remove"></i> """)
print(_("Delete"))
print("""</button>
</form>
</div>
<div id="canvas_result" style="position:relative"></div>
<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>
<div style="display:none">
""")
print('  <canvas id="new_case" width="{}px" height="{}px" style="position:absolute;top:0px;border:2px solid #000000;"></canvas>'.format(w,h))
print("""
</div>


<script>
  function erase() {""")
print('var m = confirm("',_("Delete ?"),'");')
print("""
     if (m) {
         canvas.clear();
         canvas.setBackgroundImage(img.src, canvas.renderAll.bind(canvas), {
                  originX: 'left',
                  originY: 'top',
                  left: 0,
                  top: 0
              });
     }
  }

  function resize() {
  	var canvasSizer = document.getElementById("canvasDiv");
  	var canvasScaleFactor = canvasSizer.offsetWidth/680;
  	var width = canvasSizer.offsetWidth;
  	var height = canvasSizer.offsetHeight;
  	var ratio = canvas.getWidth() /canvas.getHeight();
      if((width/height)>ratio){
       width = height*ratio;
      } else {
       height = width / ratio;
      } ;
    var scale = width / canvas.getWidth();
    var zoom = canvas.getZoom();
    zoom *= scale;
    canvas.setDimensions({ width: width, height: height });
  	canvas.setViewportTransform([zoom , 0, 0, zoom , 0, 0]);
  }

  window.addEventListener('load', resize, false);
  window.addEventListener('resize', resize, false);

  var current_color = rgb(255,0,0) ;
  var current_alpha_color = rgba(255,0,0,0.5) ;
  var current_bg_color = rgba(255,255,255,0.5) ;

  var canvas = this.__canvas = new fabric.Canvas('ma_case'
    //,{isDrawingMode: true}
  );

  canvas.freeDrawingBrush.width = 5;
  canvas.freeDrawingBrush.color = '#ff0000' ;

  var img = new Image();
  img.onload = function(){
     canvas.setBackgroundImage(img.src, canvas.renderAll.bind(canvas), {
              originX: 'left',
              originY: 'top',
              left: 0,
              top: 0
          });
  };
""")
print('  img.src = "Conversions/{}/{}";'.format(filedir,files[num]))

f = files[num]
a = f.replace(filedir,'annotation')
a = a.replace('jpg','png')
if os.path.isfile('Annotations/{}/{}'.format(filedir,a)) :

    print(' fabric.Image.fromURL("Annotations/{}/{}"'.format(filedir,a))
    print("""
        , function (oImg) {
            canvas.add(oImg);
            },{left:0,top:0,originX:'left',originY:'top'});
    """)

print("""
  </script>

  <script>


var slider1 = document.getElementById("myWidth");
var output1 = document.getElementById("demo1");""")
print("output1.innerHTML = '",_("Width :"),"'+slider1.value + ' px';")
print(""" // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider1.oninput = function() { """)
print("  output1.innerHTML = '",_("Width :"),"'+this.value + ' px';")
print("""
  canvas.freeDrawingBrush.width = this.value;
  if (canvas.getActiveObject()) {
    if (canvas.getActiveObject().get('type') === 'path') {
      canvas.getActiveObject().strokeWidth = parseInt(this.value) ;
      canvas.getActiveObject().dirty = true;
      canvas.renderAll() ;
    }
  }
}

var slider2 = document.getElementById("myAlpha");
var output2 = document.getElementById("demo2"); """)
print("output2.innerHTML = '",_("Transparency :"),"'+slider2.value + ' %';")
print(""" // Display the default slider value
var alpha = 1- slider2.value/100 ;

// Update the current slider value (each time you drag the slider handle)
slider2.oninput = function() { """)
print("  output2.innerHTML = '",_("Transparency :"),"'+this.value + ' %';")
print("""
  alpha = 1 - this.value/100 ;
  current_alpha_color = current_color.replace(")",","+alpha+")") ;
  if (canvas.getActiveObject()) {
    if (canvas.getActiveObject().get('type') === 'rect') {
      canvas.getActiveObject().fill = current_alpha_color ;
      canvas.getActiveObject().dirty = true;
      canvas.renderAll() ;
    }
  }
}

var slider3 = document.getElementById("myPolice");
var output3 = document.getElementById("demo3");""")
print("output3.innerHTML = '",_("Font Size :"),"'+slider3.value + ' px';")
print(""" // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider3.oninput = function() {""")
print("  output3.innerHTML = '",_("Font Size :"),"'+this.value + ' px';")
print("""
  if (canvas.getActiveObject()) {
    canvas.getActiveObject().fontSize = this.value ;
    canvas.renderAll() ;
  }
}

canvas.on('selection:created', updateObject);
canvas.on('selection:updated', updateObject);

</script>

  </body>
<//html>
""")
