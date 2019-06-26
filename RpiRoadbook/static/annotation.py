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
nmax = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
img_name = os.path.join(DIR,'{}_{:03d}.jpg'.format(filedir,num))
img = Image.open(img_name)
w,h = img.size

print ('Content-Type: text/html\n')
print ("""<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="w3.css">
  <link rel="stylesheet" href="font-awesome.min.css">
  <link rel="stylesheet" href="material-icons.css">


   <script type="text/javascript" src="jquery-3.3.0.min.js"></script>

   <script type="text/javascript">
      $(document).ready(function () {
         initialize();
      });

      function percentwidth(elem){
        """)
print('        return (elem.offsetWidth/{});'.format(w))
print("""
        }


      // works out the X, Y position of the click inside the canvas from the X, Y position on the page
      function getPosition(mouseEvent, sigCanvas) {
         var x, y;
         var rect = sigCanvas.getBoundingClientRect();
         var tx = percentwidth(sigCanvas)
         console.log(tx)

            //x = mouseEvent.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            //x = mouseEvent.clientX -rect.left;
            x = (mouseEvent.clientX -rect.left)/tx;
            //y = mouseEvent.clientY + document.body.scrollTop + document.documentElement.scrollTop;
            //y = mouseEvent.clientY - rect.top;
            y = (mouseEvent.clientY - rect.top)/tx;


         return { X: x , Y: y };
      }

      function initialize() {
         // get references to the canvas element as well as the 2D drawing context
         var layer1;
         var ctx1;
         var base = new Image();
""")
print('base.src="/Conversions/{}/{}_{:03d}.jpg";'.format(filedir,filedir,num))
print("""
         layer1 = document.getElementById("ma_case");
         ctx1 = layer1.getContext("2d");
""")
print('         ctx1.drawImage(base, 0, 0, {},{});'.format(w,h))
print("""
         var annot = new Image();
         var sigCanvas = document.getElementById("canvasSignature");
         var context = sigCanvas.getContext("2d");
         w = sigCanvas.width;
         h = sigCanvas.height;
         context.clearRect(0,0,w,h) ;
""")
if os.path.isfile(os.path.join('/mnt/piusb/Annotations/{}'.format(filedir),'annotation_{:03d}.png'.format(num))) :
    print('annot.src="/Annotations/{}/annotation_{:03d}.png";'.format(filedir,num)) ;
    print('context.drawImage(annot,0,0, {},{});'.format(w,h))
print("""
         context.strokeStyle = 'Red';
         context.lineWidth = 5 ;

         // This will be defined on a TOUCH device such as iPad or Android, etc.
         var is_touch_device = 'ontouchstart' in document.documentElement;

         if (is_touch_device) {
            // create a drawer which tracks touch movements
            var drawer = {
               isDrawing: false,
               touchstart: function (coors) {
                  context.beginPath();
                  context.moveTo(coors.x, coors.y);
                  this.isDrawing = true;
               },
               touchmove: function (coors) {
                  if (this.isDrawing) {
                     context.lineTo(coors.x, coors.y);
                     context.stroke();
                  }
               },
               touchend: function (coors) {
                  if (this.isDrawing) {
                     this.touchmove(coors);
                     this.isDrawing = false;
                  }
               }
            };

            // create a function to pass touch events and coordinates to drawer
            function draw(event) {

               // get the touch coordinates.  Using the first touch in case of multi-touch
               var coors = {
                  x: event.targetTouches[0].pageX,
                  y: event.targetTouches[0].pageY
               };

               // Now we need to get the offset of the canvas location
               var obj = sigCanvas;

               if (obj.offsetParent) {
                  // Every time we find a new object, we add its offsetLeft and offsetTop to curleft and curtop.
                  do {
                     coors.x -= obj.offsetLeft;
                     coors.y -= obj.offsetTop;
                  }
				  // The while loop can be "while (obj = obj.offsetParent)" only, which does return null
				  // when null is passed back, but that creates a warning in some editors (i.e. VS2010).
                  while ((obj = obj.offsetParent) != null);
               }

               // pass the coordinates to the appropriate handler
               drawer[event.type](coors);
            }


            // attach the touchstart, touchmove, touchend event listeners.
            sigCanvas.addEventListener('touchstart', draw, false);
            sigCanvas.addEventListener('touchmove', draw, false);
            sigCanvas.addEventListener('touchend', draw, false);

            // prevent elastic scrolling
            sigCanvas.addEventListener('touchmove', function (event) {
               event.preventDefault();
            }, false);
         }
         else {

            // start drawing when the mousedown event fires, and attach handlers to
            // draw a line to wherever the mouse moves to
            $("#canvasSignature").mousedown(function (mouseEvent) {
               var position = getPosition(mouseEvent, sigCanvas);

               context.moveTo(position.X, position.Y);
               context.beginPath();

               // attach event handlers
               $(this).mousemove(function (mouseEvent) {
                  drawLine(mouseEvent, sigCanvas, context);
               }).mouseup(function (mouseEvent) {
                  finishDrawing(mouseEvent, sigCanvas, context);
               }).mouseout(function (mouseEvent) {
                  finishDrawing(mouseEvent, sigCanvas, context);
               });
            });

         }
      }

      // draws a line to the x and y coordinates of the mouse event inside
      // the specified element using the specified context
      function drawLine(mouseEvent, sigCanvas, context) {

         var position = getPosition(mouseEvent, sigCanvas);

         context.lineTo(position.X, position.Y);
         context.stroke();
      }

      // draws a line from the last coordiantes in the path to the finishing
      // coordinates and unbind any event handlers which need to be preceded
      // by the mouse down event
      function finishDrawing(mouseEvent, sigCanvas, context) {
         // draw the line to the finishing coordinates
         //drawLine(mouseEvent, sigCanvas, context);

         context.closePath();

         // unbind any events which could draw
         $(sigCanvas).unbind("mousemove")
                     .unbind("mouseup")
                     .unbind("mouseout");
      }

      function erase() {
        var sigCanvas = document.getElementById("canvasSignature");
        var context = sigCanvas.getContext("2d");
        w = sigCanvas.width;
            h = sigCanvas.height;
            var m = confirm("Effacer ?");
            if (m) {
                context.clearRect(0, 0, w, h);

            }
        }

        $(function () {
               $("#save_canvas").click(function () {
                  var canvas = document.getElementById("canvasSignature")
                  var image = canvas.toDataURL("image/png");
                  image = image.replace('data:image/png;base64,', '');
                  $.ajax({
                      type : 'POST',
                      url: 'save_annotation.py',
                      data: {
                        imagedata : image ,
""")
print("                        fn : '{}',".format(filename))
print('                        num : {}'.format(num))
print("""
                      },
                       success: function (result) {
                            $( "#canvas_result" ).append( result + "<br>" );
                       }
                  });
               });
           });
   </script>
   <style>
""")
print('@media (max-width: {}px) '.format(round(w/0.9)))
print("""
{
  #ma_case,#canvasSignature,#canvasDiv {
  width: 90%;
  }

}
</style>

</head>

<body onload="initialize()">
<!-- Entete -->
<div class="w3-container w3-center w3-section w3-hide-small">
   <h1>""")
print(_("Notes"))
print("""</h1>
</div>

<div class="w3-bar">
""")
print('<a href="annotation.py?fn={}&num=0" class="w3-button"> <i class="w3-xlarge fa fa-fast-backward"></i> </a>'.format(filename) if num > 0 else '<a href="annotation.py?fn={}&num=0" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-fast-backward"></i> </a>'.format(filename))
print('<a href="annotation.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-backward"></i> </a>'.format(filename,num-10) if num-10>=0 else '<a href="annotation.py?fn={}&num={}" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-backward"></i> </a>'.format(filename,num-10))
print('<a href="annotation.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-chevron-left"></i> </a>'.format(filename,num-1) if num-1 >= 0 else '<a href="annotation.py?fn={}&num={}" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-chevron-left"></i> </a>'.format(filename,num-1))
print('<input type="text" value="{}/{}">'.format(num+1,nmax))
print('<a href="annotation.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-chevron-right"></i> </a>'.format(filename,num+1) if nmax > num+1 else '<a href="annotation.py?fn={}&num={}" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-chevron-right"></i> </a>'.format(filename,num+1))
print('<a href="annotation.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-forward"></i> </a>'.format(filename,num+10) if nmax > num+10 else '<a href="annotation.py?fn={}&num={}" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-forward"></i> </a>'.format(filename,num+10))
print('<a href="annotation.py?fn={}&num={}" class="w3-button"> <i class="w3-xlarge fa fa-fast-forward"></i> </a>'.format(filename,nmax-1) if num <nmax-1 else '<a href="annotation.py?fn={}&num={}" class="w3-button w3-disabled"> <i class="w3-xlarge fa fa-fast-forward"></i> </a>'.format(filename,nmax-1))
print("""
</div>


<div class="w3-bar w3-grey w3-center">
      <a href="#" class="w3-bar-item w3-button w3-red w3-hover-blue" id="save_canvas" name="save_canvas">""")
print(_("Save"))
print("""
</a>
      <a href="#" class="w3-bar-item w3-button w3-hover-blue" onclick="erase()" id="raz_canvas" name="raz_canvas"> """)
print(_("Clear note"))
print("""</a>
</div>
""")
print('   <div id="canvasDiv" style="position:relative;height:250px;">')
print('      <canvas id="ma_case" width="{}px" height="{}px" style="position:absolute;top:0px;border:2px solid #000000;z-index=0"></canvas>'.format(w,h))
print('      <canvas id="canvasSignature" width="{}px" height="{}px" style="position:absolute;top:0px;border:2px solid #000000;z-index=1"></canvas>'.format(w,h))
print("""
   </div>
<div id="canvas_result" style="position:relative"></div>




<!-- Pied de page -->
<div class="w3-bar w3-black">
  <a class="w3-bar-item w3-button w3-hover-blue" href="index.py"><i class="w3-xlarge fa fa-home"></i></a>
</div>

</body>

</html>
""")
