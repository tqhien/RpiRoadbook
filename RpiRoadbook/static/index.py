#!/usr/bin/python
# -*- coding: latin-1 -*-
import cgi, os
import cgitb; cgitb.enable()
import re

files = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
files.sort()

print ('Content-Type: text/html\n')
print ("<html>")
print ("<body>")
print ("<h1>Roadbooks pr&eacute;sents :</h1>")
for fileitem in files:
  
  print ('<p><a href="{}"> {} </a></p>'.format(fileitem,fileitem))
  
print ("<p></p>")
print ("<p></p>")
print ('<a href="upload.html"> <input type="button" value="T&eacute;l&eacute;charger des fichiers"></a>')
print ('<a href="setup.py"> <input type="button" value="Configuration"></a>')
print ("</body>")
print ("</html>")
