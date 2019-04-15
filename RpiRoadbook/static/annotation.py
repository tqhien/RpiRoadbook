#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import base64

form = cgi.FieldStorage()
#print(form)

if 'fn' in form:
    filename = form['fn'].value
    filedir = os.path.splitext(filename)[0]

if 'num' in form:
    num = int(form['num'].value)
else:
    num = 0

if 'nmax' in form:
    nmax = int(form['nmax'].value)

print ('Content-Type: text/html\n')
print ("""<html>
<head>
   <meta charset="utf-8" />
   <title>Annotations</title>
<link rel="stylesheet" href="/mystyle.css"/>
   <script type="text/javascript" src="jquery-3.3.0.min.js"></script>

   <script type="text/javascript">
      $(document).ready(function () {
         initialize();
      });


      // works out the X, Y position of the click inside the canvas from the X, Y position on the page
      function getPosition(mouseEvent, sigCanvas) {
         var x, y;
         var rect = sigCanvas.getBoundingClientRect();

            //x = mouseEvent.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            x = mouseEvent.clientX -rect.left;
            //y = mouseEvent.clientY + document.body.scrollTop + document.documentElement.scrollTop;
            y = mouseEvent.clientY - rect.top;


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
         ctx1.drawImage(base, 0, 0, 650,200);

         var annot = new Image();
         var sigCanvas = document.getElementById("canvasSignature");
         var context = sigCanvas.getContext("2d");
""")
if os.path.isfile('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,num)) :
    print('annot.src="/Annotations/{}/annotation_{:03d}.png";'.format(filedir,num)) ;
    print('context.drawImage(annot,0,0,650,200);')
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

</head>

<body onload="initialize()">
  <div id="main">
    <h1>Annotations</h1>
    <hr>
    <div>
""")
print('      <a href="annotation.py?fn={}&num=0&nmax={}"> <input type="button" value="|<"></a>'.format(filename,nmax))
if num-10 >=0 :
    print('      <a href="annotation.py?fn={}&num={}&nmax={}"> <input type="button" value="-10"></a>'.format(filename,num-10,nmax))
if num-1 >= 0 :
    print('      <a href="annotation.py?fn={}&num={}&nmax={}"> <input type="button" value="-1"></a>'.format(filename,num-1,nmax))
if nmax > num+1:
    print('      <a href="annotation.py?fn={}&num={}&nmax={}"> <input type="button" value="+1>"></a>'.format(filename,num+1,nmax))
if nmax > num+10 :
    print('      <a href="annotation.py?fn={}&num={}&nmax={}"> <input type="button" value="+10>"></a>'.format(filename,num+10,nmax))
print('      <a href="annotation.py?fn={}&num={}&nmax={}"> <input type="button" value=">|"></a>'.format(filename,nmax-1,nmax))
print("""
      <input type="button" id="save_canvas" name="save_canvas" value="Sauvegarder" >
      <input type="button" id="raz_canvas" name="raz_canvas" value="RAZ Annot." onclick="erase()">
    </div>
    <hr>

  <a href="index.py"> <input type="button" value="Retour &agrave; l'accueil"></a>

    <hr>
   <div id="canvasDiv" style="position:relative;height:250px;">
      <!-- It's bad practice (to me) to put your CSS here.  I'd recommend the use of a CSS file! -->
      <canvas id="ma_case"width="650px" height="200px" style="position:absolute;top:0px;border:2px solid #000000;z-index=0"></canvas>
      <canvas id="canvasSignature" width="650px" height="200px" style="position:absolute;top:0px;border:2px solid #000000;z-index=1"></canvas>

   </div>
<div id="canvas_result" style="position:relative"></div>
</div>

</body>

</html>
""")
