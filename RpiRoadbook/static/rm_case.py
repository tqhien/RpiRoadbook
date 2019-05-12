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
    num = int(form['num'].value)

DIR = '/mnt/piusb/Conversions/{}'.format(filedir)
files = [f for f in os.listdir(DIR) if re.search('.jpg$', f)]
files.sort()
f = files[num]
a = f.replace(filedir,'annotation')
a = a.replace('jpg','png')

try:
    os.remove(os.path.join(DIR,f))
    print(_('Case supprim&eacute;e'))
except :
    pass

try:
    os.remove("/mnt/piusb/Annotations/{}/{}".format(filedir,a))
    print(_('Annotation supprim&eacute;e'))
except :
    pass

print("""
</body>
</html>
""")
