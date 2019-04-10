#!/usr/bin/python
import cgi, os
import cgitb; cgitb.enable()

form = cgi.FieldStorage()

# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import convert_from_path
#import subprocess

#print ('Content-type: text/html')
#print("""
#print('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">')
print('<html>')


if 'fn' in form:
   filename = form['fn'].value
   filedir = os.path.splitext(filename)[0]
   #print(filename)

if 'page' in form:
    i = int(form['page'].value)
    #print(i)

if 'x' in form:
    x = int(form['x'].value)

if 'y' in form:
    y = int(form['y'].value)

if 'w' in form:
    w = int(form['w'].value)

if 'h' in form:
    h = int(form['h'].value)

if 'num' in form:
    num =int(form['num'].value)


if 'total' in form:
    total = int(form['total'].value)

pages = convert_from_path('/mnt/piusb/'+filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile='{:03}'.format(num),fmt='jpg')

print('Case {} / {}'.format(num+1,total))

print ('</html>')
