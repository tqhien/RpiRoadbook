#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import base64

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
    filedir = os.path.splitext(filename)[0]

if 'num' in form:
    num = int(form['num'].value)

if 'imagedata' in form:
    imageData = base64.b64decode(form['imagedata'].value)
    #imageData = form['imagedata'].value
    #imageData = bytearray([imageData])
    #print (form['imageData'].value)
    open('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,num), 'wb').write(imageData)
    print('Image annotation_{:03d}.png sauvegard&eacute;e'.format(num))
else :
    print ('no imagedata')
#print('Image sauvegardee')

print("""
</body>
</html>
""")
