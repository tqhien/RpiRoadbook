#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import base64
import re
# Pour l'internationalisation
import gettext
_ = gettext.gettext

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

if 'num' in form:
    num = form['num'].value

if 'imagedata' in form:
    imageData = base64.b64decode(form['imagedata'].value)
    #imageData = form['imagedata'].value
    #imageData = bytearray([imageData])
    #print (form['imageData'].value)
    open('/mnt/piusb/Conversions/{}/{}_.jpg'.format(filedir,num), 'wb').write(imageData)
    print(_('Case ins&eacute;r&eacute;e'))
else :
    print (_('Erreur pas de donn&eacute;es'))
#print('Image sauvegardee')

print("""
</body>
</html>
""")
