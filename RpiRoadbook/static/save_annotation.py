#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import base64
import re

form = cgi.FieldStorage()
#print(form)

print ('Content-Type: text/html\n')
print ("""<html>
<head>
<link rel="stylesheet" type="text/css" href="mystyle.css">
</head>
<body>""")

if 'fn' in form:
    filename = form['fn'].value
    filename = re.sub(r"[\s-]","-",filename)
    filedir = os.path.splitext(filename)[0]

if os.path.isdir('/mnt/piusb/Annotations/'+filedir) == False: # Pas de répertoire d'images, on cree le repertoire
    os.mkdir('/mnt/piusb/Annotations/'+filedir)

if 'num' in form:
    num = int(form['num'].value)

if 'imagedata' in form:
    imageData = base64.b64decode(form['imagedata'].value)
    #imageData = form['imagedata'].value
    #imageData = bytearray([imageData])
    #print (form['imageData'].value)
    open('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,num), 'wb').write(imageData)
    print('Image sauvegard&eacute;e')
else :
    print ('no imagedata')
#print('Image sauvegardee')

print("""
</body>
</html>
""")
