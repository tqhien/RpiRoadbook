#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 08:58:53 2018

@author: Hien TRAN-QUANG

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>

Ce programme est un logiciel libre ; vous pouvez le redistribuer ou le modifier
suivant les termes de la GNU General Public License telle que publiée par la
Free Software Foundation ; soit la version 3 de la licence, soit (à votre gré)
toute version ultérieure.

Ce programme est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE GARANTIE ;
sans même la garantie tacite de QUALITÉ MARCHANDE ou d'ADÉQUATION à UN BUT PARTICULIER.
Consultez la GNU General Public License pour plus de détails.

Vous devez avoir reçu une copie de la GNU General Public License en même temps que ce programme ;
si ce n'est pas le cas, consultez <http://www.gnu.org/licenses>

Ce programme s'appuie sur la bibliothèque gratuit et open-source Pygame pour Python : <http://www.pygame.org>
et s'est inspiré de <https://nerdparadise.com/programming/pygame/part7> pour la class d'objet des scènes
"""

# Pour masquer le message de la version de pygame
#import contextlib
#with contextlib.redirect_stdout(None):
import pygame.display

# Pour l'affichage sur le framebuffer
from pygame.locals import *

import time
import datetime
import os
import configparser
import re
# import serial
# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import page_count,convert_from_path,page_size
import subprocess

import RPi.GPIO as GPIO

# Pour la gestion du touchscreen
import sys
if os.path.isdir ("/dev/input/event0") :
    os.environ["SDL_FBDEV"] = "/dev/fb0"
    os.environ["SDL_MOUSEDRV"] = "TSLIB"
    os.environ["SDL_MOUSEDEV"] = "/dev/input/event0"
    is_tactile = True
else:
    is_tactile = False

fps = 5

distance = 0
totalisateur = 0
speed = 0
old_totalisateur = 0

distance1 = 0
vmoy1 = 0
vmax1 = 0
#chrono_delay1 = 5 * aimants # 5 tours de roue avant de declencher le chrono
chrono_delay1 = 5
chrono_time1 = 0
old_distance1 = 0

distance2 = 0
vmoy2 = 0
vmax2 = 0
#chrono_delay2 = 5 * aimants # 5 tours de roue avant de declencher le chrono
chrono_delay2 = 5
chrono_time2 = 0
old_distance2 = 0

decompte = 2
start_decompte = False
chrono_decompte = 0

roue = 1864
aimants = 1
developpe = 1.0*roue / aimants
orientation = 'Paysage'
ncases = 3
force_refresh = False

save_t_moy = time.time()
save_t_odo = time.time()
old_t = time.time()
temperature = -1
cpu = -1

nb_screens = 4

filedir = ''
fichiers = []

rb_ratio = 1

CAPTEUR_ROUE    = USEREVENT # Odometre
BOUTON_LEFT     = pygame.K_LEFT # Bouton left (tout en haut)
BOUTON_HOME     = pygame.K_HOME # Bouton left long
BOUTON_RIGHT    = pygame.K_RIGHT # Bouton right (2eme en haut)
BOUTON_END      = pygame.K_END # Bouton right long
BOUTON_OK       = pygame.K_RETURN # Bouton OK/select (au milieu)
BOUTON_BACKSPACE = pygame.K_BACKSPACE # Bouton OK long
BOUTON_UP       = pygame.K_UP # Bouton Up (1er en bas)
BOUTON_PGUP     = pygame.K_PAGEUP # Bouton UP long
BOUTON_DOWN     = pygame.K_DOWN # Bouton Down (tout en bas)
BOUTON_PGDOWN  = pygame.K_PAGEDOWN # Bouton Down long

GPIO_ROUE = 17
GPIO_LEFT = 27
GPIO_OK   = 22
GPIO_RIGHT = 23
GPIO_UP = 24
GPIO_DOWN = 25

left_state = False
ok_state = False
right_state = False
up_state = False
down_state = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_ROUE, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Capteur de vitesse
GPIO.setup(GPIO_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Test bouton au démarrage pour menu de configuration
gotoConfig = not GPIO.input(GPIO_OK)

#*******************************************************************************************************#
#------------------------- Les callbacks des interruptions GPIO et fonctions utiles --------------------#
#*******************************************************************************************************#
def input_roue_callback(channel):
    global totalisateur,distance,developpe
    global distance1,chrono_delay1,chrono_time1
    global distance2,chrono_delay2,chrono_time2
    global chronoconfig

    totalisateur += developpe
    distance += developpe
    distance1 += developpe
    distance2 += developpe

    # gestion du demarrage du chrono1
    # Valeur > 1 : on attend de faire suffisamment de tours de roue
    # Valeur = 1 : on demarre le chrono1
    # Valeur = 0 : le chrono1 est demarre
    chrono_delay1 -= 1
    if chrono_delay1 < 0 :
        chrono_delay1 = 0
    # Test si on doit demarrer le chrono1
    if chrono_delay1 == 1 :
        chrono_time1 = time.time()
        chrono_delay1 = 0
        chronoconfig['Chronometre1']['chrono_delay'] = str(chrono_delay1)
        chronoconfig['Chronometre1']['chrono_time'] = str(chrono_time1)
        save_chronoconfig()

    # Idem chrono2
    chrono_delay2 -= 1
    if chrono_delay2 < 0 :
        chrono_delay2 = 0
    # Test si on doit demarrer le chrono2
    if chrono_delay2 == 1 :
        chrono_time2 = time.time()
        chrono_delay2 = 0
        chronoconfig['Chronometre2']['chrono_delay'] = str(chrono_delay2)
        chronoconfig['Chronometre2']['chrono_time'] = str(chrono_time2)
        save_chronoconfig()


def input_left_callback(channel):
    global left_state
    left_long_state = False
    b4_time = time.time()
    t = time.time() - b4_time
    while not GPIO.input(channel) :# on attend le retour du bouton
        if t >= .05 and t < 2:
            if not left_state:
                left_state = True
        if t >=2:
            if not left_long_state:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_HOME}))
                left_long_state = True
                old_t = time.time() - b4_time
            else:
                if t - old_t >= .5 :
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_HOME}))
                    old_t = time.time() - b4_time
        t = time.time() - b4_time
    if t >= .05 and t < 2:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_LEFT}))
    left_state = False
    left_long_state = False


def input_right_callback(channel):
    global right_state
    right_long_state = False
    b4_time = time.time()
    t = time.time() - b4_time
    while not GPIO.input(channel) :# on attend le retour du bouton
        if t >= .05 and t < 2:
            if not right_state:
                right_state = True
        if t >=2 :
            if not right_long_state:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_END}))
                right_long_state = True
                old_t = time.time() - b4_time
            else:
                if t - old_t >= .5 :
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_END}))
                    old_t = time.time() - b4_time
        t = time.time() - b4_time
    if t >= .05 and t < 2:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_RIGHT}))
    right_state = False
    right_long_state = False


def input_ok_callback(channel):
    global ok_state
    ok_long_state = False
    b4_time = time.time()
    t = time.time() - b4_time
    while not GPIO.input(channel) :# on attend le retour du bouton
        if t >= .05 and t < 2:
            if not ok_state:
                ok_state = True
        if t >=2 :
            if not ok_long_state:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_BACKSPACE}))
                ok_long_state = True
        t = time.time() - b4_time
    if t >= .05 and t < 2:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_OK}))
    ok_state = False
    ok_long_state = False

def input_up_callback(channel):
    global up_state
    up_long_state = False
    b4_time = time.time()
    t = time.time() - b4_time
    while not GPIO.input(channel) :# on attend le retour du bouton
        if t >= .05 and t < 2:
            if not up_state:
                up_state = True
        if t >=2 :
            if not up_long_state:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGUP}))
                up_long_state = True
                old_t = time.time() - b4_time
            else:
                if t - old_t >= .5 :
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGUP}))
                    old_t = time.time() - b4_time
        t = time.time() - b4_time
    if t >= .05 and t < 2:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_UP}))
    up_state = False
    up_long_state = False

def input_down_callback(channel):
    global down_state
    down_long_state = False
    b4_time = time.time()
    t = time.time() - b4_time
    while not GPIO.input(channel) :# on attend le retour du bouton
        if t >= .05 and t < 2:
            if not down_state:
                down_state = True
        if t >=2 :
            if not down_long_state:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGDOWN}))
                down_long_state = True
                old_t = time.time() - b4_time
            else:
                if t - old_t >= .5 :
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGDOWN}))
                    old_t = time.time() - b4_time
        t = time.time() - b4_time
    if t >= .05 and t < 2:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_DOWN}))
    down_state = False
    down_long_state = False


#On définit les interruptions sur les GPIO des commandes
GPIO.add_event_detect(GPIO_ROUE, GPIO.FALLING, callback=input_roue_callback,bouncetime=15)
GPIO.add_event_detect(GPIO_LEFT, GPIO.FALLING, callback=input_left_callback, bouncetime=50)
GPIO.add_event_detect(GPIO_RIGHT, GPIO.FALLING, callback=input_right_callback, bouncetime=50)
GPIO.add_event_detect(GPIO_OK, GPIO.FALLING, callback=input_ok_callback, bouncetime=50)
GPIO.add_event_detect(GPIO_UP, GPIO.FALLING, callback=input_up_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_DOWN, GPIO.FALLING, callback=input_down_callback, bouncetime=300)

#*******************************************************************************************************#
#------------------------- Le callbacks des suivis systeme : temp et cpu -------------------------------#
#*******************************************************************************************************#

def rpi_temp():
    global temperature
    try:
        tfile = open('/sys/class/thermal/thermal_zone0/temp')
        t = tfile.read()
        temperature = float(t)/1000
        tfile.close()
    except:
        temperature = -1

def cpu_load():
    global cpu
    try:
        with open ('/proc/loadavg','r') as f:
            cpu = int(float(f.readline().split(" ")[:3][0])*100)
    except:
        cpu = -1

#-----------------------------------------------------------------------------------------------#
#----------------------------- Gestion des images en cache -------------------------------------#
#-----------------------------------------------------------------------------------------------#
image_cache = {}
def get_image(key,angle=0,mode_jour=True):
    global filedir,fichiers,image_cache
    # Chargement des images uniquement si pas encore en cache
    if not (key,angle,mode_jour) in image_cache:
        img = pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[key]))
        if mode_jour:
            s = img
        else :
            s = pygame.Surface(img.get_rect().size, pygame.SRCALPHA)
            s.fill((255,255,0,200))
            s.blit(img, (0,0), None, BLEND_RGB_SUB)
        if os.path.isfile('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,key)) :
            annot = pygame.image.load('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,key)).convert()
            annot.set_colorkey(NOIR)
            s.blit(annot,(0,0))
        image_cache[(key,angle)] = pygame.transform.rotozoom (s,angle,rb_ratio)
    return image_cache[(key,angle)]


#-------------------------------------------------------------------------------------------#
#------------------------------ Optimisation des rendus des textes -------------------------#
#-------------------------------------------------------------------------------------------#

mode_jour = True
# Definition des couleurs
BLANC = (255,255,255)
NOIR = (0,0,0)
ROUGE = (255,0,0)
VERT = (0,255,0)
BLEU = (0,0,255)
GRIS = (125,125,125)
JAUNE = (200,200,50,100)

#Styles utilises :
BLANC25     = 0
BLANC50     = 1
BLANC75     = 2
BLANC100    = 3
BLANC200    = 4
BLANC25inv  = 5
BLANC50inv  = 6
ROUGE25     = 7
ROUGE25inv  = 8
VERT25      = 9
GRIS75      =10
BLANC80     =11
BLANC20     =12
ROUGE20     =13
BLANC3      =14
BLANC4      =15
BLANC5      =16
ROUGE3      =17
ROUGE4      =18
ROUGE5      =19
VERT3       =20
VERT4       =21
VERT5       =22
BLANC20inv  =23
BLANC3inv   =24
BLANC4inv   =25
BLANC5inv   =26
#Taille des polices pour chaque style
SALPHA = {BLANC25:25,BLANC50:50,BLANC75:75,BLANC100:100,BLANC200:200,BLANC25inv:25,BLANC50inv:50,ROUGE25:25,ROUGE25inv:25,VERT25:25,GRIS75:75,BLANC80:80,BLANC20:20,BLANC20inv:20,ROUGE20:20,BLANC3:90,BLANC3inv:90,BLANC4:59,BLANC4inv:59,BLANC5:45,BLANC5inv:45,ROUGE3:90,ROUGE4:59,ROUGE5:45,VERT3:90,VERT4:59,VERT5:45}

alphabet = {}
alphabet_size_x = {}
alphabet_size_y = {}

myfont = {}
def load_font(police=BLANC25) :
    global myfont
    # Chargement d'une font si pas encore en cache
    if not police in myfont :
        if police in SALPHA:
            myfont[police]  = pygame.font.SysFont("cantarell", SALPHA[police])
        else :
            myfont[police]  = pygame.font.SysFont("cantarell", 25)


labels = {}
old_labels = {}

def setup_alphabet(police=BLANC25):
    global alphabet,alphabet_size_x,alphabet_size_y,myfont,angle
    load_font(police)
    #printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ àâäçéèêëîïôöùûü'
    printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
    fg_jour = { BLANC25:NOIR,  BLANC50:NOIR,  BLANC75:NOIR,  BLANC100:NOIR,  BLANC200:NOIR,  BLANC25inv:BLANC, BLANC50inv:BLANC, ROUGE25:ROUGE, ROUGE25inv:BLANC, VERT25:BLEU,  GRIS75:GRIS, BLANC80:NOIR, BLANC20:NOIR,ROUGE20:ROUGE,BLANC3:NOIR,BLANC4:NOIR,BLANC5:NOIR,ROUGE3:ROUGE,ROUGE4:ROUGE,ROUGE5:ROUGE,VERT3:VERT,VERT4:VERT,VERT5:VERT,BLANC20inv:BLANC,BLANC3inv:BLANC,BLANC4inv:BLANC,BLANC5inv:BLANC}
    bg_jour = { BLANC25:BLANC, BLANC50:BLANC, BLANC75:BLANC, BLANC100:BLANC, BLANC200:BLANC, BLANC25inv:NOIR,  BLANC50inv:NOIR,  ROUGE25:BLANC, ROUGE25inv:ROUGE, VERT25:BLANC, GRIS75:BLANC, BLANC80:BLANC, BLANC20:BLANC,ROUGE20:BLANC,BLANC3:BLANC,BLANC4:BLANC,BLANC5:BLANC,ROUGE3:BLANC,ROUGE4:BLANC,ROUGE5:BLANC,VERT3:BLANC,VERT4:BLANC,VERT5:BLANC,BLANC20inv:NOIR,BLANC3inv:NOIR,BLANC4inv:NOIR,BLANC5inv:NOIR}
    fg_nuit = { BLANC25:JAUNE, BLANC50:JAUNE, BLANC75:JAUNE, BLANC100:JAUNE, BLANC200:JAUNE, BLANC25inv:NOIR,  BLANC50inv:NOIR,  ROUGE25:ROUGE, ROUGE25inv:ROUGE,  VERT25:VERT,  GRIS75:GRIS, BLANC80:JAUNE, BLANC20:JAUNE,ROUGE20:JAUNE,BLANC3:JAUNE,BLANC4:JAUNE,BLANC5:JAUNE,ROUGE3:ROUGE,ROUGE4:ROUGE,ROUGE5:ROUGE,VERT3:VERT,VERT4:VERT,VERT5:VERT,BLANC20inv:NOIR,BLANC3inv:NOIR,BLANC4inv:NOIR,BLANC5inv:NOIR}
    bg_nuit = { BLANC25:NOIR,  BLANC50:NOIR,  BLANC75:NOIR,  BLANC100:NOIR,  BLANC200:NOIR,  BLANC25inv:BLANC, BLANC50inv:BLANC, ROUGE25:NOIR,  ROUGE25inv:BLANC, VERT25:NOIR,  GRIS75:NOIR, BLANC80:NOIR, BLANC20:NOIR,ROUGE20:NOIR,BLANC3:NOIR,BLANC4:NOIR,BLANC5:NOIR,ROUGE3:NOIR,ROUGE4:NOIR,ROUGE5:NOIR,VERT3:NOIR,VERT4:NOIR,VERT5:NOIR,BLANC20inv:BLANC,BLANC3inv:BLANC,BLANC4inv:BLANC,BLANC5inv:BLANC}


    if mode_jour :
        if angle == 90 :
            for i in printable :
                alphabet[(i,police,angle)] = pygame.transform.rotate (myfont[police].render(i,1,fg_jour[police],bg_jour[police]),90)
                alphabet_size_x[(i,police,angle)] = 0
                alphabet_size_y[(i,police,angle)] = -alphabet[(i,police,angle)].get_size()[1]
        else :
            for i in printable :
                alphabet[(i,police,angle)] = myfont[police].render(i,1,fg_jour[police],bg_jour[police])
                alphabet_size_x[(i,police,angle)] = alphabet[(i,police,angle)].get_size()[0]
                alphabet_size_y[(i,police,angle)] = 0
        alphabet[(' ',police,angle)].fill(bg_jour[police])
    else :
        if angle == 90 :
            for i in printable :
                alphabet[(i,police,angle)] = pygame.transform.rotate (myfont[police].render(i,1,fg_nuit[police],bg_nuit[police]),90)
                alphabet_size_x[(i,police,angle)] = 0
                alphabet_size_y[(i,police,angle)] = -alphabet[(i,police,angle)].get_size()[1]
        else :
            for i in printable :
                alphabet[(i,police,angle)] = myfont[police].render(i,1,fg_nuit[police],bg_nuit[police])
                alphabet_size_x[(i,police,angle)] = alphabet[(i,police,angle)].get_size()[0]
                alphabet_size_y[(i,police,angle)] = 0
        alphabet[(' ',police,angle)].fill(bg_nuit[police])

def blit_text (screen,st,coords, col=BLANC25,angle=0):
    if (not angle in (0,90)) : angle = 0
    (x,y) = coords
    if angle == 0 :
        for i in st :
            r = screen.blit(alphabet[(i,col,angle)],(x,y))
            x += alphabet_size_x[(i,col,angle)]
            y += alphabet_size_y[(i,col,angle)]
            pygame.display.update(r)
    else :
        for i in st :
            x += alphabet_size_x[(i,col,angle)]
            y += alphabet_size_y[(i,col,angle)]
            r = screen.blit(alphabet[(i,col,angle)],(x,y))
            pygame.display.update(r)

def update_labels(screen):
    global labels,old_labels
    for i in list(labels.keys()) :
       if (i not in old_labels.keys()) or (old_labels [i] != labels[i]) :
            if (i in old_labels.keys()) and (len(old_labels[i][0]) > len (labels[i][0])) :
                 blit_text (screen,' '*len(old_labels[i][0]),old_labels[i][1],old_labels[i][2],old_labels[i][3])
            blit_text (screen,labels[i][0],labels[i][1],labels[i][2],labels[i][3])
#            emit('Rallye',{i : labels[i][0]})
            old_labels [i] = labels[i]

#--------------------------------------------------------------------------------- ----------#
#------------------------------ Optimisation des rendus des sprites -------------------------#
#---------------------------------------------------------------------------------- ---------#

sprites = {}
old_sprites = {}

def blit_sprite (screen,sprite,coords):
    r = screen.blit(sprite,coords)
    pygame.display.update(r)

def update_sprites(screen):
    global sprites,old_sprites,force_refresh
    for i in list(sprites.keys()) :
        if (i not in old_sprites.keys()) or (old_sprites [i] != sprites[i]) or force_refresh :
            blit_sprite (screen,sprites[i][0],sprites[i][1])
            #emit(i,sprites[i][0])
            old_sprites [i] = sprites[i]
            force_refresh = False

#--------------------------------------------------------------------------------- ----------#
#------------------------------ Organisation des widgets ------------------------------------#
#---------------------------------------------------------------------------------- ---------#
current_screen = 1
current_widget = 0
old_widget = 1
widgets = {}
nb_widgets = 1

#------------------------------ Definition des widgets ---------------------------------------------#
widget_presets = {
    'pajra1' : {'orientation':'Paysage','jour_nuit':'Jour','mode':'Rallye','layout':'1'},
    'pajra2' : {'orientation':'Paysage','jour_nuit':'Jour','mode':'Rallye','layout':'2'},
    'pajra3' : {'orientation':'Paysage','jour_nuit':'Jour','mode':'Rallye','layout':'3'},
    'pajra4' : {'orientation':'Paysage','jour_nuit':'Jour','mode':'Rallye','layout':'4'},
    'panra1' : {'orientation':'Paysage','jour_nuit':'Nuit','mode':'Rallye','layout':'1'},
    'panra2' : {'orientation':'Paysage','jour_nuit':'Nuit','mode':'Rallye','layout':'2'},
    'panra3' : {'orientation':'Paysage','jour_nuit':'Nuit','mode':'Rallye','layout':'3'},
    'panra4' : {'orientation':'Paysage','jour_nuit':'Nuit','mode':'Rallye','layout':'4'},
    'pojra1' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Rallye','layout':'5'},
    'pojra2' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Rallye','layout':'6'},
    'pojra3' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Rallye','layout':'7'},
    'pojra4' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Rallye','layout':'8'},
    'pojra5' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Rallye','layout':'9'},
    'pojra6' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Rallye','layout':'10'},
    'ponra1' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Rallye','layout':'5'},
    'ponra2' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Rallye','layout':'6'},
    'ponra3' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Rallye','layout':'7'},
    'ponra4' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Rallye','layout':'8'},
    'ponra5' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Rallye','layout':'9'},
    'ponra6' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Rallye','layout':'10'},
    'pajro1' : {'orientation':'Paysage','jour_nuit':'Jour','mode':'Route','layout':'11'},
    'panro1' : {'orientation':'Paysage','jour_nuit':'Nuit','mode':'Route','layout':'11'},
    'pojro1' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Route','layout':'12'},
    'pojro1' : {'orientation':'Portrait','jour_nuit':'Nuit','mode':'Route','layout':'12'},
    'pajzz' : {'orientation':'Paysage','jour_nuit':'Jour','mode':'Zoom','layout':'0'},
    'pojzz' : {'orientation':'Portrait','jour_nuit':'Jour','mode':'Zoom','layout':'00'},
}

widget_sizes = {
    # Nb de champs pour les formats rallye paysage
    '1' : 3,
    '2' : 4,
    '3' : 5,
    '4' : 6,
    # Nb de champs pour les formats rallye portrait
    '5' : 2,
    '6' : 3,
    '7' : 4,
    '8' : 1,
    '9' : 2,
    '10': 3,
    # Nb de champs pour les compteurs simples paysage et portrait
    '11': 5,
    '12': 5,
    # Pour le zoom
    '0' : 0,
    '00': 0
    }

widget_layouts = {
    '0' : [
        {'x':500,'y':0,'w':300,'h':30,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':0,'y1':1,'x2':120,'y2':1,'x3':240,'y3':1}],
    '00' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE20,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100}],
    '1' : [
        {'x':500,'y':0,'w':300,'h':30,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':1,'x2':120,'y2':1,'x3':240,'y3':1},
        {'x':500,'y':30,'w':300,'h':150,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':5,'y1':115,'x2':15,'y2':1,'x3':240,'y3':115},
        {'x':500,'y':180,'w':300,'h':150,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':5,'y1':115,'x2':15,'y2':1,'x3':240,'y3':115},
        {'x':500,'y':330,'w':300,'h':150,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':5,'y1':115,'x2':15,'y2':1,'x3':240,'y3':115}],
    '2' : [
        {'x':500,'y':0,'w':300,'h':30,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':1,'x2':120,'y2':1,'x3':240,'y3':1},
        {'x':500,'y':30,'w':300,'h':110,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':75,'x2':100,'y2':1,'x3':240,'y3':75},
        {'x':500,'y':140,'w':300,'h':110,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':75,'x2':100,'y2':1,'x3':240,'y3':75},
        {'x':500,'y':250,'w':300,'h':110,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':75,'x2':100,'y2':1,'x3':240,'y3':75},
        {'x':500,'y':360,'w':300,'h':110,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':75,'x2':100,'y2':1,'x3':240,'y3':75}],
    '3' : [
        {'x':500,'y':0,'w':300,'h':30,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':1,'x2':120,'y2':1,'x3':240,'y3':1},
        {'x':500,'y':30,'w':300,'h':90,'label_font':ROUGE25,'value_font':BLANC5,'unit_font':BLANC25,'over_font':ROUGE5,'inside_font':VERT5,'selected_font':BLANC5inv,'x1':150,'y1':1,'x2':5,'y2':20,'x3':150,'y3':40},
        {'x':500,'y':120,'w':300,'h':90,'label_font':ROUGE25,'value_font':BLANC5,'unit_font':BLANC25,'over_font':ROUGE5,'inside_font':VERT5,'selected_font':BLANC5inv,'x1':150,'y1':1,'x2':5,'y2':20,'x3':150,'y3':40},
        {'x':500,'y':210,'w':300,'h':90,'label_font':ROUGE25,'value_font':BLANC5,'unit_font':BLANC25,'over_font':ROUGE5,'inside_font':VERT5,'selected_font':BLANC5inv,'x1':150,'y1':1,'x2':5,'y2':20,'x3':150,'y3':40},
        {'x':500,'y':300,'w':300,'h':90,'label_font':ROUGE25,'value_font':BLANC5,'unit_font':BLANC25,'over_font':ROUGE5,'inside_font':VERT5,'selected_font':BLANC5inv,'x1':150,'y1':1,'x2':5,'y2':20,'x3':150,'y3':40},
        {'x':500,'y':390,'w':300,'h':90,'label_font':ROUGE25,'value_font':BLANC5,'unit_font':BLANC25,'over_font':ROUGE5,'inside_font':VERT5,'selected_font':BLANC5inv,'x1':150,'y1':1,'x2':5,'y2':20,'x3':150,'y3':40}],
    '4' : [
        {'x':500,'y':0,'w':300,'h':30,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':1,'x2':120,'y2':1,'x3':240,'y3':1},
        {'x':500,'y':30,'w':300,'h':75,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':25,'x2':155,'y2':25,'x3':240,'y3':25},
        {'x':500,'y':105,'w':300,'h':75,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':25,'x2':155,'y2':25,'x3':240,'y3':25},
        {'x':500,'y':180,'w':300,'h':75,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':25,'x2':155,'y2':25,'x3':240,'y3':25},
        {'x':500,'y':255,'w':300,'h':75,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':25,'x2':155,'y2':25,'x3':240,'y3':25},
        {'x':500,'y':330,'w':300,'h':75,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':25,'x2':155,'y2':25,'x3':240,'y3':25},
        {'x':500,'y':405,'w':300,'h':75,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':25,'x2':155,'y2':25,'x3':240,'y3':25}],
    '5' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':0,'w':150,'h':480,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':1,'y1':480,'x2':20,'y2':380,'x3':1,'y3':70},
        {'x':180,'y':0,'w':150,'h':480,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':1,'y1':480,'x2':20,'y2':380,'x3':1,'y3':70}],
    '6' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':0,'w':150,'h':480,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':1,'y1':475,'x2':1,'y2':320,'x3':1,'y3':70},
        {'x':180,'y':240,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':180,'y':0,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70}],
    '7' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':240,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':30,'y':0,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':180,'y':240,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':180,'y':0,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70}],
    '8' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':0,'w':150,'h':480,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':1,'y1':475,'x2':30,'y2':320,'x3':1,'y3':70}],
    '9' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':240,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':30,'y':0,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70}],
    '10' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':240,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':30,'y':0,'w':75,'h':240,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':30,'y3':70},
        {'x':105,'y':0,'w':75,'h':240,'label_font':ROUGE25,'value_font':BLANC25,'unit_font':BLANC25,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC25inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':30,'y3':70}],
    '11' : [
        {'x':0,'y':0,'w':300,'h':30,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':1,'x2':120,'y2':1,'x3':240,'y3':1},
        {'x':0,'y':30,'w':300,'h':150,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':5,'y1':115,'x2':15,'y2':1,'x3':240,'y3':115},
        {'x':0,'y':180,'w':300,'h':150,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':5,'y1':115,'x2':15,'y2':1,'x3':240,'y3':115},
        {'x':0,'y':330,'w':300,'h':150,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':5,'y1':115,'x2':15,'y2':1,'x3':240,'y3':115},
        {'x':300,'y':0,'w':500,'h':300,'label_font':ROUGE25,'value_font':BLANC200,'unit_font':BLANC25,'over_font':BLANC200,'inside_font':BLANC200,'selected_font':BLANC200,'x1':5,'y1':265,'x2':100,'y2':1,'x3':440,'y3':265},
        {'x':300,'y':300,'w':500,'h':180,'label_font':ROUGE25,'value_font':BLANC100,'unit_font':BLANC25,'over_font':BLANC100,'inside_font':BLANC100,'selected_font':BLANC200,'x1':5,'y1':130,'x2':100,'y2':1,'x3':440,'y3':130}],
    '12' : [
        {'x':0,'y':0,'w':30,'h':480,'label_font':ROUGE20,'value_font':BLANC20,'unit_font':ROUGE20,'over_font':ROUGE25,'inside_font':VERT25,'selected_font':BLANC20inv,'x1':1,'y1':400,'x2':1,'y2':280,'x3':1,'y3':100},
        {'x':30,'y':0,'w':150,'h':480,'label_font':ROUGE25,'value_font':BLANC3,'unit_font':BLANC25,'over_font':ROUGE3,'inside_font':VERT3,'selected_font':BLANC3inv,'x1':1,'y1':475,'x2':1,'y2':320,'x3':1,'y3':70},
        {'x':180,'y':240,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':180,'y':0,'w':150,'h':240,'label_font':ROUGE25,'value_font':BLANC4,'unit_font':BLANC25,'over_font':ROUGE4,'inside_font':VERT4,'selected_font':BLANC4inv,'x1':1,'y1':235,'x2':30,'y2':200,'x3':100,'y3':70},
        {'x':330,'y':0,'w':300,'h':480,'label_font':ROUGE25,'value_font':BLANC200,'unit_font':BLANC25,'over_font':BLANC200,'inside_font':BLANC200,'selected_font':BLANC200,'x1':1,'y1':475,'x2':40,'y2':400,'x3':1,'y3':70},
        {'x':630,'y':0,'w':170,'h':480,'label_font':ROUGE25,'value_font':BLANC100,'unit_font':BLANC25,'over_font':BLANC100,'inside_font':BLANC200,'selected_font':BLANC200,'x1':1,'y1':480,'x2':40,'y2':400,'x3':1,'y3':70}],
}


class rb_widget():
    def __init__(self,layout='1',widget=0):
        global angle
        self.widget_order = widget
        angle = 0 if layout in ('0','1','2','3','4','11') else 90
        a = widget_layouts[layout][widget]
        setup_alphabet(a['label_font'])
        setup_alphabet(a['value_font'])
        setup_alphabet(a['unit_font'])
        setup_alphabet(a['selected_font'])

        self.selected_font = a['selected_font']
        self.label_font = a['label_font']
        self.value_font = a['value_font']
        self.unit_font = a['unit_font']
        self.over_font = a['over_font']
        self.inside_font = a['inside_font']

        (self.x,self.y) = (a['x'],a['y'])
        (self.w,self.h) = (a['w'],a['h'])
        (self.x1,self.y1) = (a['x1'],a['y1'])
        (self.x2,self.y2) = (a['x2'],a['y2'])
        (self.x3,self.y3) = (a['x3'],a['y3'])
        self.selected = False
    def upup(self):
        pass
    def up(self):
        pass
    def down(self):
        pass
    def downdown(self):
        pass
    def ok(self):
        global current_widget,nb_widgets
        current_widget += 1
        if current_widget > nb_widgets :
            current_widget = 0
    def reset(self):
        pass
    def update(self):
        pass
    def render(self,scr):
        if self.selected:
           r = pygame.draw.rect(scr,ROUGE,(self.x,self.y,self.w,self.h),1)
        else:
           r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)
    def select(self):
        self.selected = True
    def deselect(self):
        self.selected = False


def widget_dispatch(st,layout,widget):
    if st == 'Totalisateur' :
        return odo_widget(layout,widget)
    elif st == 'Trip1' :
        return trip1_widget(layout,widget)
    elif st == 'Trip2' :
        return trip2_widget(layout,widget)
    elif st == 'Vitesse' :
        return speed_widget(layout,widget)
    elif st == 'Vmoy1' :
        return vmoy1_widget(layout,widget)
    elif st == 'Vmoy2' :
        return vmoy2_widget(layout,widget)
    elif st == 'Vmax1' :
        return vmax1_widget(layout,widget)
    elif st == 'Vmax2' :
        return vmax2_widget(layout,widget)
    elif st == 'Chrono1' :
        return chrono1_widget(layout,widget)
    elif st == 'Chrono2' :
        return chrono2_widget(layout,widget)
    elif st == 'Decompte' :
        return countdown_widget(layout,widget)
    elif st == 'Heure' :
        return heure_widget(layout,widget)
    else :
        return rb_widget(layout,widget)

#------------------ Affichage de l'heure, de la charge cpu et de la temperature du rpi ------------------------------#
#------ Actions possibles : changement d'affichage personnalise sur appui long ok (reset)-----------------------------------#
class status_widget (rb_widget):
    def __init__(self,layout='0',widget=0):
        global angle
        rb_widget.__init__(self,layout,widget)
    def reset(self):
        global widgets,current_screen,screenconfig,nb_widgets,ncases,sprites,old_sprites,mode_jour,force_refresh

        # On charge le mode en cours, le roadbook en cours et sa case
        candidates = ['/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
        rbconfig.read(candidates)
        rallye = rbconfig['Mode']['mode']

        current_screen += 1
        if current_screen > nb_screens :
            current_screen = 1
        form =  screenconfig['Affichage{}'.format(current_screen)]['layout']
        mode_j = screenconfig['Affichage{}'.format(current_screen)]['jour_nuit'] == 'Jour'
        if mode_j != mode_jour :
            mode_jour = mode_j
            alphabet = {}
        t = 'pa' if orientation == 'Paysage' else 'po'
        t += 'j' if mode_jour else 'n'
        if rallye == 'Rallye' :
            t += 'ra'
            t += form
        elif rallye == 'Zoom':
            t += 'zz'
        else:
            t += 'ro1'
        preset = widget_presets[t]
        layout = preset['layout']
        nb_widgets = widget_sizes [layout]
        if layout in ('00','8','9','10'):
            ncases = 4
        else:
            ncases = 3
        widgets = {}
        sprites = {}
        force_refresh = True
        #old_sprites = {}
        
        widgets[(0)] = status_widget(layout,0)
        for i in range(1,nb_widgets+1) :
            widgets[(i)] = widget_dispatch(screenconfig['Affichage{}'.format(current_screen)]['ligne{}'.format(i)],layout,i)
        if mode_jour :
            pygame.display.get_surface().fill(BLANC)
        else :
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()
        for j in list(widgets.keys()):
            widgets[j].update()
    def update(self):
        self.now = time.localtime()
    def render(self,scr):
        global angle,temperature,cpu
        blit_text(scr,'{:3.0f}C  '.format(temperature),(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:02d}:{:02d}:{:02d}'.format(self.now.tm_hour,self.now.tm_min,self.now.tm_sec),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:02d}:{:02d}:{:02d}'.format(self.now.tm_hour,self.now.tm_min,self.now.tm_sec),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'{:02.0f}%  '.format(cpu),(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage du totalisateur                                             ------------------------------#
#------ Actions possibles : aucun                                                    -----------------------------------#
class odo_widget (rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def render(self,scr):
        global angle
        blit_text(scr,' Totalisateur',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:05.0f}'.format(totalisateur/1000000),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:05.0f}'.format(totalisateur/1000000),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage de la vitesse instantanee                                             ------------------------------#
#------ Actions possibles : aucun                                                    -----------------------------------#
class speed_widget (rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def update(self):
        global totalisateur,speed,save_t_moy,old_totalisateur
        k = time.time()
        if ( k - save_t_moy >= 1) : # Vitesse moyenne sur 1 seconde
            speed = (totalisateur-old_totalisateur)*3.6/(k-save_t_moy)/1000;
            save_t_moy = k
            old_totalisateur = totalisateur
    def render(self,scr):
        global angle
        blit_text(scr,' Vitesse',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:3.0f} '.format(speed),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:3.0f} '.format(speed),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km/h',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage du trip1                                          ------------------------------#
#------ Actions possibles : remise a zero , ajustement +/-100m                  -----------------------------------#
class trip1_widget (rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def upup(self):
        global distance1,old_distance1
        distance1+=1000000
        old_distance1=distance1
        odoconfig['Odometre']['Distance1'] = str(distance1)
        save_odoconfig()
    def up(self):
        global distance1,old_distance1
        distance1+=10000
        old_distance1=distance1
        odoconfig['Odometre']['Distance1'] = str(distance1)
        save_odoconfig()
    def down(self):
        global distance1,old_distance1
        distance1-=10000
        if distance1<0:
            distance1 = 0
        old_distance1=distance1
        odoconfig['Odometre']['Distance1'] = str(distance1)
        save_odoconfig()
    def downdown(self):
        global distance1,old_distance1
        distance1-=1000000
        if distance1<0:
            distance1 = 0
        old_distance1=distance1
        odoconfig['Odometre']['Distance1'] = str(distance1)
        save_odoconfig()
    def reset(self):
        global distance1,old_distance1,vmoy1,speed,vmax1,chrono_delay1,chrono_time1
        global odoconfig,chronoconfig
        global save_t_moy,save_t_odo
        distance1 = 0
        old_distance1 = distance1
        vmoy1 = 0
        speed = 0
        vmax1 = 0
        chrono_delay1 = 5 * aimants
        chrono_time1 = 0
        odoconfig['Odometre']['Totalisateur'] = str(totalisateur)
        odoconfig['Odometre']['Distance1'] = str(distance1)
        chronoconfig['Chronometre1']['chrono_delay'] = str(chrono_delay1)
        chronoconfig['Chronometre1']['chrono_time'] = str(chrono_time1)
        save_odoconfig()
        save_chronoconfig()
        save_t_moy = time.time()
        save_t_odo = time.time()
    def render(self,scr):
        global angle
        blit_text(scr,' Trip1',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:6.2f}'.format(distance1/1000000),(self.x+self.x2,self.y+self.y2),self.selected_font,angle)
        else:
            blit_text(scr,'{:6.2f}'.format(distance1/1000000),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage de la vitesse moyenne sur le trip1                                             ------------------------------#
#------ Actions possibles : aucun (il faut faire un RAZ du Trip1 pour remettre a zero)                                                    -----------------------------------#
class vmoy1_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def update(self):
        global vmoy1,chrono_time1
        temps = time.time() - chrono_time1
        if temps <= 2 :
            vmoy1 = 0
        else :
            vmoy1 = distance1 * 3.6 / temps / 1000
    def render(self,scr):
        global angle
        blit_text(scr,' Vmoy1',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:3.0f} '.format(vmoy1),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:3.0f} '.format(vmoy1),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km/h',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage de la vitesse moyenne1                                             ------------------------------#
#------ Actions possibles : aucun                                                    -----------------------------------#
class vmax1_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def update(self):
        global speed,vmax1
        temps = time.time() - chrono_time1
        if temps <= 2 :
            speed = 0
        else :
            speed = distance1 * 3.6 / temps / 1000
        if speed > vmax1 :
            vmax1 = speed
    def render(self,scr):
        global angle
        blit_text(scr,' Vmax1',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:03.0f} '.format(vmax1),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:03.0f} '.format(vmax1),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km/h',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage du chrono1                                            ------------------------------#
#------ Actions possibles : aucun                                                    -----------------------------------#
class chrono1_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def reset(self):
        global distance1,chrono_delay1,chrono_time1
        global odoconfig,chronoconfig
        distance1 = 0
        chrono_delay1 = 5 * aimants
        chrono_time1 = 0
        odoconfig['Odometre']['Totalisateur'] = str(totalisateur)
        odoconfig['Odometre']['Distance1'] = str(distance1)
        chronoconfig['Chronometre1']['chrono_delay'] = str(chrono_delay1)
        chronoconfig['Chronometre1']['chrono_time'] = str(chrono_time1)
        save_odoconfig()
        save_chronoconfig()
    def render(self,scr):
        global angle,chrono_time1
        if chrono_time1 != 0:
             t = time.time() - chrono_time1
        else:
             t = 0
        m,s = divmod (t,60)
        if m >= 100 :
            h,m = divmod (m,100)
        ss = (s*100) % 100
        blit_text(scr,' Chrono1',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:02.0f}:{:02.0f}'.format(m,s),(self.x+self.x2,self.y+self.y2),self.selected_font,angle)
        else:
            blit_text(scr,'{:02.0f}:{:02.0f}'.format(m,s),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'.{:02.0f}  '.format(ss),(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

class trip2_widget (rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def upup(self):
        global distance2,old_distance2
        distance2+=1000000
        old_distance2=distance2
        odoconfig['Odometre']['Distance2'] = str(distance2)
        save_odoconfig()
    def up(self):
        global distance2,old_distance2
        distance2+=10000
        old_distance2=distance2
        odoconfig['Odometre']['Distance2'] = str(distance2)
        save_odoconfig()
    def down(self):
        global distance2,old_distance2
        distance2-=10000
        if distance2<0:
            distance2 = 0
        old_distance2=distance2
        odoconfig['Odometre']['Distance2'] = str(distance2)
        save_odoconfig()
    def downdown(self):
        global distance2,old_distance2
        distance2-=1000000
        if distance2<0:
            distance2 = 0
        old_distance2=distance2
        odoconfig['Odometre']['Distance2'] = str(distance2)
        save_odoconfig()
    def reset(self):
        global distance2,old_distance2,vmoy2,speed,vmax2,chrono_delay2,chrono_time2
        global odoconfig,chronoconfig
        global save_t_moy,save_t_odo
        distance2 = 0
        old_distance2 = distance2
        vmoy2 = 0
        vmax2 = 0
        chrono_delay2 = 5 * aimants
        chrono_time2 = 0
        odoconfig['Odometre']['Totalisateur'] = str(totalisateur)
        odoconfig['Odometre']['Distance2'] = str(distance2)
        chronoconfig['Chronometre2']['chrono_delay'] = str(chrono_delay2)
        chronoconfig['Chronometre2']['chrono_time'] = str(chrono_time2)
        save_odoconfig()
        save_chronoconfig()
        save_t_moy = time.time()
        save_t_odo = time.time()
    def render(self,scr):
        global angle
        blit_text(scr,' Trip2',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:6.2f}'.format(distance2/1000000),(self.x+self.x2,self.y+self.y2),self.selected_font,angle)
        else:
            blit_text(scr,'{:6.2f}'.format(distance2/1000000),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

class vmoy2_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def update(self):
        global vmoy2,chrono_time2
        temps = time.time() - chrono_time2
        if temps <= 2 :
            vmoy2 = 0
        else :
            vmoy2 = distance2 * 3.6 / temps /1000
    def render(self,scr):
        global angle
        blit_text(scr,' Vmoy2',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:03.0f} '.format(vmoy2),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:03.0f} '.format(vmoy2),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km/h',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

class vmax2_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def update(self):
        global speed,vmax2
        temps = time.time() - chrono_time2
        if temps <= 2 :
            speed = 0
        else :
            speed = distance2 * 3.6 / temps / 1000
        if speed > vmax2 :
            vmax2 = speed
    def render(self,scr):
        global angle
        blit_text(scr,' Vmax2',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:03.0f} '.format(vmax2),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:03.0f} '.format(vmax2),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'km/h',(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

class chrono2_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def reset(self):
        global distance2,chrono_delay2,chrono_time2
        global odoconfig,chronoconfig
        distance2 = 0
        chrono_delay2 = 5 * aimants
        chrono_time2 = 0
        odoconfig['Odometre']['Totalisateur'] = str(totalisateur)
        odoconfig['Odometre']['Distance2'] = str(distance2)
        chronoconfig['Chronometre2']['chrono_delay'] = str(chrono_delay2)
        chronoconfig['Chronometre2']['chrono_time'] = str(chrono_time2)
        save_odoconfig()
        save_chronoconfig()
    def render(self,scr):
        global angle,chrono_time2
        if chrono_time2 != 0:
             t = time.time() - chrono_time2
        else:
             t=0
        m,s = divmod (t,60)
        if m >= 100:
            h,m = divmod (m,100)
        ss = (s*100) % 100
        blit_text(scr,' Chrono2',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:02.0f}:{:02.0f}'.format(m,s),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:02.0f}:{:02.0f}'.format(m,s),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'.{:02.0f} '.format(ss),(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#------------------ Affichage du compte a rebours                                            ------------------------------#
#------ Actions possibles : ajout de 30 secondes, RAZ, demarrage du compte a rebours                                                    -----------------------------------#
class countdown_widget (rb_widget):
    def __init__(self,layout='1',widget=0):
        global decompte
        rb_widget.__init__(self,layout,widget)
        setup_alphabet(self.over_font)
        setup_alphabet(self.inside_font)
        decompte = 0
    def up(self):
        global decompte
        decompte += 30
    def down(self):
        global start_decompte,chrono_decompte
        start_decompte = True
        chrono_decompte = time.time() + decompte
    def reset(self):
        global decompte,start_decompte,chrono_decompte
        decompte = 0
        start_decompte = False
        chrono_decompte = 0
    def render(self,scr):
        global angle
        if start_decompte:
            t = chrono_decompte - time.time()
            if t <=30 and t >= 0 :
                self.value_font = self.inside_font
            if t < 0 :
                self.value_font = self.over_font
                self.unit_font = self.label_font
                t = -t
        else:
            t = decompte
        m,s = divmod (t,60)
        ss = (s*100) % 100
        blit_text(scr,' Decompte',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:02.0f}:{:02.0f} '.format(m,s),(self.x+self.x2,self.y+self.y2),self.selected_font,angle)
        else:
            blit_text(scr,'{:02.0f}:{:02.0f} '.format(m,s),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'.{:02.0f} '.format(ss),(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

class heure_widget(rb_widget):
    def __init__(self,layout='1',widget=0):
        rb_widget.__init__(self,layout,widget)
    def update(self):
        self.now = time.localtime()
    def render(self,scr):
        global angle,chrono_time2
        blit_text(scr,' Heure',(self.x+self.x1,self.y+self.y1), self.label_font,angle)
        if self.selected:
            blit_text(scr,'{:02d}:{:02d}'.format(self.now.tm_hour,self.now.tm_min),(self.x+self.x2,self.y+self.y2),self.selected_font, angle)
        else:
            blit_text(scr,'{:02d}:{:02d}'.format(self.now.tm_hour,self.now.tm_min),(self.x+self.x2,self.y+self.y2),self.value_font, angle)
        blit_text(scr,'{:02.0f} '.format(self.now.tm_sec),(self.x+self.x3,self.y+self.y3),self.unit_font,angle)
        r = pygame.draw.rect(scr,GRIS,(self.x,self.y,self.w,self.h),1)
        pygame.display.update(r)

#----------------------------------------------------------------------------------------------#
#-------------------------- Vérification configfiles ------------------------------------------#
#----------------------------------------------------------------------------------------------#
setupconfig = configparser.ConfigParser()
guiconfig = configparser.ConfigParser()
rbconfig = configparser.ConfigParser()
odoconfig = configparser.ConfigParser()
chronoconfig = configparser.ConfigParser()
screenconfig = configparser.ConfigParser()
routecongig = configparser.ConfigParser()

def save_setupconfig():
    global setupconfig
    for attempt in range(5):
        try :
            with open('/mnt/piusb/.conf/RpiRoadbook_setup.cfg', 'w') as configfile:
                setupconfig.write(configfile)
        except :
            subprocess.Popen('sudo mount -a',shell=True)
            time.sleep(.2)
        else :
            break
    else :
        print('Write Error RpiRoadbook_setup.cfg after 5 tries')

def save_rbconfig():
    global rbconfig
    for attempt in range(5):
        try :
            with open('/mnt/piusb/.conf/RpiRoadbook.cfg', 'w') as configfile:
                rbconfig.write(configfile)
        except :
            subprocess.Popen('sudo mount -a',shell=True)
            time.sleep(.2)
        else :
            break
    else :
        print('Write Error RpiRoadbook.cfg after 5 tries')

def save_odoconfig():
    global odoconfig
    for attempt in range (5):
        try:
            with open('/mnt/piusb/.log/odo.cfg','w') as configfile:
                odoconfig.write(configfile)
        except:
            subprocess.Popen('sudo mount -a',shell=True)
            time.sleep(.2)
        else :
            break
    else :
        print('Write Error odo.cfg after 5 tries')

def save_chronoconfig():
    global chronoconfig
    for attempt in range (5):
        try:
            with open('/mnt/piusb/.log/chrono.cfg','w') as configfile:
                chronoconfig.write(configfile)
        except:
            subprocess.Popen('sudo mount -a',shell=True)
            time.sleep(.2)
        else :
            break
    else :
        print('Write Error chrono.cfg after 5 tries')

def save_screenconfig(mode='Route'):
    global screenconfig
    f = '/mnt/piusb/.conf/route.cfg' if mode == 'Route' else '/mnt/piusb/.conf/screen.cfg'
    for attempt in range (5):
        try:
            with open(f,'w') as configfile:
                screenconfig.write(configfile)
        except:
            subprocess.Popen('sudo mount -a',shell=True)
            time.sleep(.2)
        else :
            break
    else :
        print('Write Error screen.cfg after 5 tries')


def check_configfile():
    global guiconfig,setupconfig,mode_jour,rbconfig,odoconfig,chronoconfig,screenconfig
    global totalisateur,old_totalisateur,distance1,distance2,developpe,aimants,chrono_delay1,chrono_time1,chrono_delay2,chrono_time2,orientation
    global widgets,nb_widgets,ncases
    # On charge les emplacements des elements d'affichage
    guiconfig.read('/home/rpi/RpiRoadbook/gui.cfg')

    # On charge les reglages : developpe, nb aimants, orientation
    candidates = ['/home/rpi/RpiRoadbook/setup.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
    setupconfig.read(candidates)
    save_setupconfig()
    aimants = setupconfig['Parametres']['aimants']
    developpe = float(setupconfig['Parametres']['roue']) / float(setupconfig['Parametres']['aimants'])
    orientation = setupconfig['Parametres']['orientation']

    # On charge le mode en cours, le roadbook en cours et sa case
    candidates = ['/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
    rbconfig.read(candidates)
    save_rbconfig()
    rallye = rbconfig['Mode']['mode']

    # On charge le trip
    candidates = ['/home/rpi/RpiRoadbook/odo.cfg','/mnt/piusb/.log/odo.cfg']
    odoconfig.read(candidates)
    save_odoconfig()
    totalisateur = float(odoconfig['Odometre']['Totalisateur'])
    old_totalisateur = totalisateur
    distance1 = float(odoconfig['Odometre']['Distance1'])
    distance2 = float(odoconfig['Odometre']['Distance2'])

    # On charge le chrono pour la vitesse moyenne
    candidates = ['/home/rpi/RpiRoadbook/chrono.cfg','/mnt/piusb/.log/chrono.cfg']
    chronoconfig.read(candidates)
    save_chronoconfig()
    chrono_delay1 = int (chronoconfig['Chronometre1']['chrono_delay'])
    chrono_time1 = float(chronoconfig['Chronometre1']['chrono_time'])
    chrono_delay2 = int (chronoconfig['Chronometre2']['chrono_delay'])
    chrono_time2 = float(chronoconfig['Chronometre2']['chrono_time'])

    # On charge les configuration d'ecran selon le mode
    if rallye == 'Route' :
        candidates = ['/home/rpi/RpiRoadbook/route.cfg','/mnt/piusb/.conf/route.cfg']
    else:
        candidates = ['/home/rpi/RpiRoadbook/screen.cfg','/mnt/piusb/.conf/screen.cfg']
    screenconfig.read(candidates)
    save_screenconfig(rallye)
    mode_jour = screenconfig['Affichage1']['jour_nuit'] == 'Jour'
    form =  screenconfig['Affichage{}'.format(current_screen)]['layout']
    t = 'pa' if orientation == 'Paysage' else 'po'
    t += 'j' if mode_jour else 'n'
    if rallye == 'Rallye' :
        t += 'ra'
        t += form
    elif rallye == 'Zoom':
        t += 'zz'
    else:
        t += 'ro1'
    preset = widget_presets[t]
    layout = preset['layout']
    if layout in ('00','8','9','10'):
        ncases = 4
    else:
        ncases = 3
    nb_widgets = widget_sizes [layout]
    widgets[(0)] = status_widget(layout,0)
    for i in range(1,nb_widgets+1) :
        widgets[(i)] = widget_dispatch(screenconfig['Affichage{}'.format(current_screen)]['ligne{}'.format(i)],layout,i)



#*******************************************************************************************************#
#---------------------------------------- Le template de classe / écran  -------------------------------#
#*******************************************************************************************************#
class SceneBase:
    def __init__(self, fname = ''):
        self.next = self
        self.filename = fname
        #pygame.display.get_surface().fill((0,0,0))
        #pygame.display.update()

    def ProcessInput(self, events, pressed_keys):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)

#*******************************************************************************************************#
#--------------------------------------- La boucle principale de l'appli -------------------------------#
#*******************************************************************************************************#
def run_RpiRoadbook(width, height,  starting_scene):
    global fps
    pygame.display.init()

    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()
    pygame.font.init()


    active_scene = starting_scene
    check_configfile()
    t_sys = time.time()
    rpi_temp()
    cpu_load()

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        # On ne checke la température et la charge cpu que toutes les 5 secondes
        if time.time() - 5 > t_sys :
            rpi_temp()
            cpu_load()
            t_sys = time.time()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)

        active_scene = active_scene.next

#        pygame.display.update()
        clock.tick(fps)
    GPIO.cleanup()

#*******************************************************************************************************#
#---------------------------------------- Ecran Titre du Roadbook --------------------------------------#
#*******************************************************************************************************#

class TitleScene(SceneBase):
    def __init__(self, fname = ''):
        pygame.font.init()
        check_configfile()

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        global gotoConfig
        if gotoConfig :
            gotoConfig = False
            self.SwitchToScene(ModeScene())
        else :
            self.rallye = rbconfig['Mode']['mode']
            if self.rallye in ('Rallye','Zoom') :
                self.SwitchToScene(SelectionScene())
            elif self.rallye == 'Route' :
                self.SwitchToScene(OdometerScene())

    def Render(self, screen):
        if mode_jour :
            screen.fill(BLANC)
        else :
            screen.fill(NOIR)
        pygame.display.update()


#*******************************************************************************************************#
#---------------------------------------- Ecran de sélection du Roadbook -------------------------------#
#*******************************************************************************************************#
class SelectionScene(SceneBase):
    def __init__(self):
        global angle,labels,old_labels,sprites,old_sprites,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self)

        self.runonce=True

        #pygame.font.init()
        check_configfile()


        self.orientation = setupconfig['Parametres']['orientation']

        angle = 90 if self.orientation == 'Portrait' else 0

        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}

        # On ne charge que les polices dont on a besoin
        setup_alphabet(BLANC25)
        setup_alphabet(BLANC25inv)
        setup_alphabet(ROUGE25)
        setup_alphabet(ROUGE25inv)
        setup_alphabet(VERT25)

        self.gotoEdit = False

        if self.orientation == 'Paysage' :
            labels['infos'] = ('Demarrage automatique dans 5s...',(int(guiconfig[self.orientation]['select_text_x']),int(guiconfig[self.orientation]['select_text_y'])),VERT25,angle)
            labels['invite'] = ('Selectionnez le roadbook a charger :',(10,10),BLANC25,angle)
            labels['up'] = ('        ',(10,50),BLANC25,angle)
            labels['down'] = ('        ',(10,380),BLANC25,angle)
            for i in range (10) :
                labels['liste{}'.format(i)] = ('',(10,80+i*30),BLANC25,angle)
        else :
            labels['infos'] = ('Demarrage automatique dans 5s...',(int(guiconfig[self.orientation]['select_text_x']),int(guiconfig[self.orientation]['select_text_y'])),VERT25,angle)
            labels['invite'] = ('Selectionnez le roadbook a charger :',(0,480),BLANC25,angle)
            labels['up'] = ('        ',(50,480),BLANC25,angle)
            labels['down'] = ('        ',(380,480),BLANC25,angle)
            for i in range (10) :
                labels['liste{}'.format(i)] = ('',(80+i*30,480),BLANC25,angle)

        self.countdown = 5 ;
        self.iscountdown = True ;
        self.selection= 0 ;
        self.fenetre = 0 ;
        self.saved = rbconfig['Roadbooks']['etape'] ;
        self.filenames = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
        if len(self.filenames) == 0 : self.SwitchToScene(NoneScene())
        if self.saved in self.filenames : # le fichier rb existe, on le préselectionne
            self.filename = self.saved
            self.selection = self.filenames.index(self.filename)
        else : # le fichier rb n'existe plus
            self.filename = ''

        self.column = 1

        if mode_jour :
            self.menu_edit_white = pygame.image.load('./images/icone_edit_white_selected.jpg')
            self.menu_edit = pygame.image.load('./images/icone_edit_white.jpg')
            pygame.display.get_surface().fill(BLANC)
        else :
            self.menu_edit = pygame.image.load('./images/icone_edit.jpg')
            self.menu_edit_white = pygame.image.load('./images/icone_edit_selected.jpg')
            pygame.display.get_surface().fill(NOIR)
        if is_tactile :
            sprites['edit'] = (self.menu_edit,(int(guiconfig[self.orientation]['select_edit_x']),int(guiconfig[self.orientation]['select_edit_y'])))
        pygame.display.update()
        self.j = time.time()


    def ProcessInput(self, events, pressed_keys):
        global rbconfig
        for event in events:
            if event.type == pygame.KEYDOWN :
                self.iscountdown = False
                if event.key == BOUTON_UP :
                    self.iscountdown = False
                    if self.column ==1 : self.selection -= 1
                    if self.selection < 0: self.selection = 0
                    if self.selection < self.fenetre: self.fenetre -= 1
                    if self.fenetre < 0 : self.fenetre = 0
                elif event.key == BOUTON_DOWN :
                    self.iscountdown = False
                    if self.column == 1 : self.selection += 1
                    if self.selection == len(self.filenames): self.selection = len(self.filenames)-1
                    if self.selection >= self.fenetre+10: self.fenetre+=1
                elif event.key == BOUTON_LEFT :
                    self.iscountdown = False
                    if is_tactile:
                        self.column -= 1
                    if self.column < 1 : self.column = 2
                elif event.key == BOUTON_RIGHT :
                    self.iscountdown = False
                    if is_tactile:
                        self.column += 1
                    if self.column > 2 : self.column = 1
                elif event.key == BOUTON_OK :
                        self.iscountdown = False ;
                        if self.column == 1 :
                            if self.filename != self.filenames[self.selection] : # on a sélectionné un nouveau rb, on va se positionner au début
                                self.filename = self.filenames[self.selection]
                                rbconfig['Roadbooks']['etape'] = self.filenames[self.selection]
                                rbconfig['Roadbooks']['case'] = '0'
                                save_rbconfig()
                            self.k = self.j + self.countdown + 1 # hack pour afficher le message chargement en cours
                            self.SwitchToScene(ConversionScene(self.filename))
                        else :
                            self.filename = self.filenames[self.selection]
                            self.gotoEdit = True

    def Update(self):
        global sprites,old_sprites,labels,old_labels,angle, rbconfig
        if self.gotoEdit :
            self.SwitchToScene(EditScene(self.filename))
        else :
            # Mise à jour de la liste de choix
            if self.fenetre > 0 :
                labels['up'] = ('(moins)',labels['up'][1],labels['up'][2],labels['up'][3])

            for i in range (10) :
                if self.next == self :
                    labels['liste{}'.format(i)] = ('                                                ',labels['liste{}'.format(i)][1],BLANC25,angle)
            for i in range (len(self.filenames)) :
                if i >= self.fenetre and i <self.fenetre+10 :
                    p = 'liste{}'.format(i-self.fenetre)
                    if self.filenames[i] == self.saved :
                        text = self.filenames[i]+' (En cours)'
                        if i == self.selection :
                            couleur = ROUGE25inv
                        else :
                            couleur = ROUGE25
                    else :
                        text = self.filenames[i]
                        if i == self.selection :
                            couleur = BLANC25inv
                        else :
                            couleur = BLANC25
                    if self.next == self :
                        labels[p] = (text,labels[p][1],couleur,labels[p][3])
            if self.fenetre+10<len(self.filenames):
                labels['down'] = ('(plus)',labels['down'][1],labels['down'][2],labels['down'][3])

            self.k = time.time()
            if self.next == self:
                if is_tactile:
                   sprites['edit'] = (self.menu_edit_white,sprites['edit'][1]) if self.column == 2 else (self.menu_edit,sprites['edit'][1])
            if self.iscountdown :
                if self.k-self.j< self.countdown :
                    #print(labels['infos'])
                    #labels['infos'] = ('{}'.format('Chargement'),labels['infos'][1],labels['infos'][2],labels['infos'][3])
                #else :
                    if self.next == self :
                        labels['infos'] = ('Demarrage automatique dans {:1.0f}s...'.format(self.countdown+1-(self.k-self.j)),labels['infos'][1],labels['infos'][2],labels['infos'][3])
            else :
                if self.next == self :
                    labels['infos'] = ('                                                         ',labels['infos'][1],labels['infos'][2],labels['infos'][3])

            if self.iscountdown:
                self.k = time.time();
                if (self.k-self.j>=self.countdown) :
                    rbconfig['Roadbooks']['etape'] = self.filenames[self.selection]
                    save_rbconfig()
                    self.SwitchToScene(ConversionScene(self.filename))


    def Render(self, screen):
        update_labels(screen)
        update_sprites(screen)

#*******************************************************************************************************#
#---------------------------------------- La partie Pas de Roadbooks présents --------------------------#
#*******************************************************************************************************#
class NoneScene(SceneBase):
    def __init__(self, fname = ''):
        global labels,old_labels,sprites,old_sprites,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        labels = {}
        old_labels = {}

        setup_alphabet(ROUGE25)

        if mode_jour :
            pygame.display.get_surface().fill(BLANC)
        else :
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()

        #self.img = pygame.image.load('./../Roadbooks/images/nothing.jpg')
        labels['text1'] = ('Aucun roadbook present.', (100,200),ROUGE25,0)
        labels['text2'] = ('Appuyez sur un bouton pour revenir', (100,230),ROUGE25,0)
        labels['text3'] = ('au menu en mode Route', (100,260),ROUGE25,0)

    def ProcessInput(self, events, pressed_keys):
        global setupconfig
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            elif event.type == pygame.KEYDOWN :
                if event.key == BOUTON_LEFT or event.key == BOUTON_RIGHT or event.key == BOUTON_OK or event.key == BOUTON_UP or event.key == BOUTON_DOWN :
                    setupconfig['Parametres']['mode'] = 'Route'
                    save_setupconfig()
                    self.SwitchToScene(TitleScene())

    def Update(self):
        pass

    def Render(self, screen):
        update_labels(screen)

#*******************************************************************************************************#
#---------------------------------------- La partie Mode -----------------------------------------------#
#*******************************************************************************************************#
class ModeScene(SceneBase):
    def __init__(self, fname = ''):
        global setupconfig,rbconfig,angle,labels,old_labels,sprites,old_sprites, mode_jour,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        #check_configfile()

        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}

        self.now = time.localtime()
        self.orientation = setupconfig['Parametres']['orientation']

        angle = 90 if self.orientation == 'Portrait' else 0

        setup_alphabet(BLANC50)
        setup_alphabet(BLANC50inv)

        labels ['t_mode'] = ('Mode :',(int(guiconfig[self.orientation]['mode_l_mode_x']),int(guiconfig[self.orientation]['mode_l_mode_y'])),BLANC50,angle)
        labels ['mode'] = ('Rallye',(int(guiconfig[self.orientation]['mode_mode_x']),int(guiconfig[self.orientation]['mode_mode_y'])),BLANC50,angle)
        labels ['t_nuit'] = ('Jour/Nuit :',(int(guiconfig[self.orientation]['mode_l_jour_nuit_x']),int(guiconfig[self.orientation]['mode_l_jour_nuit_y'])),BLANC50,angle)
        labels ['jour_nuit'] = ('Rallye',(int(guiconfig[self.orientation]['mode_jour_nuit_x']),int(guiconfig[self.orientation]['mode_jour_nuit_y'])),BLANC50,angle)
        labels ['t_orientation'] = ('Orientation :',(int(guiconfig[self.orientation]['mode_l_orientation_x']),int(guiconfig[self.orientation]['mode_l_orientation_y'])),BLANC50,angle)
        labels ['orientation'] = ('Portrait ',(int(guiconfig[self.orientation]['mode_orientation_x']),int(guiconfig[self.orientation]['mode_orientation_y'])),BLANC50,angle)

        labels ['suivant'] = ('->',(int(guiconfig[self.orientation]['mode_suiv_x']),int(guiconfig[self.orientation]['mode_suiv_y'])),BLANC50,angle)

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.index = 0 # 0= mode, 1=nuit, 2=orientation, 3=suivant, 4 = ok

        self.rallye = rbconfig['Mode']['mode']
        mode_jour = screenconfig['Affichage1']['jour_nuit'] == 'Jour'
        self.paysage = setupconfig['Parametres']['orientation'] == 'Paysage'

        if mode_jour :
            if angle == 0 :
                self.bouton_ok_white = pygame.image.load('./images/ok.jpg')
                self.bouton_ok = pygame.image.load('./images/ok_white.jpg')
            else :
                self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
                self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
            pygame.display.get_surface().fill(BLANC)
        else:
            if angle == 0 :
                self.bouton_ok = pygame.image.load('./images/ok.jpg')
                self.bouton_ok_white = pygame.image.load('./images/ok_white.jpg')
            else :
                self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
                self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
            pygame.display.get_surface().fill(NOIR)
        sprites ['ok'] = (self.bouton_ok,(int(guiconfig[self.orientation]['mode_ok_x']),int(guiconfig[self.orientation]['mode_ok_y'])))
        pygame.display.update()

    def ProcessInput(self, events, pressed_keys):
        global setupconfig,rbconfig,mode_jour,alphabet,alphabet_size_x,alphabet_size_y,old_labels, old_sprites
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == BOUTON_RIGHT:
                    self.index+=1
                    if self.index > 5:
                        self.index = 0
                elif event.key == BOUTON_LEFT:
                    self.index -= 1
                    if self.index < 0 :
                        self.index = 5
                elif event.key == BOUTON_DOWN:
                    if self.index == 0 :
                        if self.rallye == 'Rallye' :
                            self.rallye = 'Route'
                        elif self.rallye == 'Route' :
                            self.rallye = 'Zoom'
                        elif self.rallye == 'Zoom' :
                            self.rallye = 'Rallye'
                        rbconfig['Mode']['mode'] = self.rallye
                        save_rbconfig()

                    elif self.index == 1 :
                        mode_jour = not mode_jour
                        screenconfig['Affichage1']['jour_nuit'] = 'Jour' if mode_jour else 'Nuit'
                        save_setupconfig()

                    elif self.index == 2 :
                        self.paysage = not self.paysage
                        setupconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        if self.paysage :
                            subprocess.Popen('sudo mount /dev/root / -o rw,remount',shell=True)
                            subprocess.Popen('sudo cp -f /root/asplash_paysage.sh /root/asplash.sh',shell=True)
                            subprocess.Popen('sudo mount /dev/root / -o ro,remount', shell=True)
                        else :
                            subprocess.Popen('sudo mount /dev/root / -o rw,remount',shell=True)
                            subprocess.Popen('sudo cp -f /root/asplash_portrait.sh /root/asplash.sh',shell=True)
                            subprocess.Popen('sudo mount /dev/root / -o ro,remount',shell=True)
                        save_setupconfig()

                elif event.key == BOUTON_UP:
                    if self.index ==0:
                        if self.rallye == 'Rallye' :
                            self.rallye = 'Zoom'
                        elif self.rallye == 'Zoom' :
                            self.rallye = 'Route'
                        elif self.rallye == 'Route' :
                            self.rallye = 'Rallye'
                        setupconfig['Parametres']['mode'] = self.rallye
                        save_setupconfig()

                    elif self.index == 1:
                        mode_jour = not mode_jour
                        setupconfig['Parametres']['jour_nuit'] = 'Jour' if mode_jour else 'Nuit'
                        save_setupconfig

                    elif self.index == 2 :
                        self.paysage = not self.paysage
                        setupconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        if self.paysage :
                            subprocess.Popen('sudo mount /dev/root / -o rw,remount',shell=True)
                            subprocess.Popen('sudo cp -f /root/asplash_paysage.sh /root/asplash.sh',shell=True)
                            subprocess.Popen('sudo mount /dev/root / -o ro,remount',shell=True)
                        else :
                            subprocess.Popen('sudo mount /dev/root / -o rw,remount',shell=True)
                            subprocess.Popen('sudo cp -f /root/asplash_portrait.sh /root/asplash.sh',shell=True)
                            subprocess.Popen('sudo mount /dev/root / -o ro,remount',shell=True)
                        save_setupconfig()

                elif event.key == BOUTON_OK:
                    # validation
                    if self.index == 0:
                        setupconfig['Parametres']['mode'] = self.rallye
                        save_setupconfig()
                    elif self.index == 1:
                        setupconfig['Parametres']['jour_nuit'] = 'Jour' if mode_jour else 'Nuit'
                        save_setupconfig()
                    elif self.index == 2:
                        setupconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        if self.paysage :
                            subprocess.Popen('sudo mount /dev/root / -o rw,remount',shell=True)
                            subprocess.Popen('sudo cp -f /root/asplash_paysage.sh /root/asplash.sh',shell=True)
                            subprocess.Popen('sudo mount /dev/root / -o ro,remount',shell=True)
                        else :
                            subprocess.Popen('sudo mount /dev/root / -o rw,remount',shell=True)
                            subprocess.Popen('sudo cp -f /root/asplash_portrait.sh /root/asplash.sh',shell=True)
                            subprocess.Popen('sudo mount /dev/root / -o ro,remount',shell=True)
                        save_setupconfig()
                    elif self.index == 3 :
                        self.SwitchToScene(ConfigScene())
                    elif self.index == 4 :
                        alphabet = {}
                        alphabet_size_x = {}
                        alphabet_size_y = {}
                        setup_alphabet()
                        self.SwitchToScene(TitleScene())
                    # on passe au réglage suivant
                    self.index +=1
                    if self.index > 2:
                        self.index = 0

    def Update(self):
        global labels,old_labels,sprites,old_sprites
        if self.next == self :
            labels['mode'] = (self.rallye,labels['mode'][1],BLANC50inv,labels['mode'][3]) if self.index == 0 else (self.rallye,labels['mode'][1],BLANC50,labels['mode'][3])

            if mode_jour :
                labels['jour_nuit'] = ('Jour   ',labels['jour_nuit'][1],BLANC50inv,labels['jour_nuit'][3]) if self.index == 1 else ('Jour   ',labels['jour_nuit'][1],BLANC50,labels['jour_nuit'][3])
            else :
                labels['jour_nuit'] = ('Nuit   ',labels['jour_nuit'][1],BLANC50inv,labels['jour_nuit'][3]) if self.index == 1 else ('Nuit   ',labels['jour_nuit'][1],BLANC50,labels['jour_nuit'][3])

            if self.paysage :
                labels['orientation'] = ('Paysage',labels['orientation'][1],BLANC50inv,labels['orientation'][3]) if self.index == 2 else ('Paysage ',labels['orientation'][1],BLANC50,labels['orientation'][3])
            else :
                labels['orientation'] = ('Portrait ',labels['orientation'][1],BLANC50inv,labels['orientation'][3]) if self.index == 2 else ('Portrait ',labels['orientation'][1],BLANC50,labels['orientation'][3])

            labels ['suivant'] = ('->',labels['suivant'][1],BLANC50inv,labels['suivant'][3]) if self.index == 3 else ('->',labels['suivant'][1],BLANC50,labels['suivant'][3])
            sprites['ok'] = (self.bouton_ok_white,sprites['ok'][1]) if self.index == 4 else (self.bouton_ok,sprites['ok'][1])

    def Render(self, screen):
        update_labels(screen)
        update_sprites(screen)


#*******************************************************************************************************#
#---------------------------------------- La partie Réglages -------------------------------------------#
#*******************************************************************************************************#
class ConfigScene(SceneBase):
    def __init__(self, fname = ''):
        global angle,labels,old_labels,sprites,old_sprites,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        #check_configfile()

        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}

        self.now = time.localtime()
        self.orientation = setupconfig['Parametres']['orientation']

        angle = 90 if self.orientation == 'Portrait' else 0

        setup_alphabet(BLANC50)
        setup_alphabet(BLANC50inv)

        labels ['t_roue'] = ('Roue :',(int(guiconfig[self.orientation]['config_l_roue_x']),int(guiconfig[self.orientation]['config_l_roue_y'])),BLANC50,angle)
        labels ['roue'] = ('{:4d}'.format(0),(int(guiconfig[self.orientation]['config_roue_x']),int(guiconfig[self.orientation]['config_roue_y'])),BLANC50,angle)
        labels ['t_aimants'] = ('Nb aimants :',(int(guiconfig[self.orientation]['config_l_aimants_x']),int(guiconfig[self.orientation]['config_l_aimants_y'])),BLANC50,angle)
        labels ['aimants'] = ('{:2d}  '.format(0),(int(guiconfig[self.orientation]['config_aimants_x']),int(guiconfig[self.orientation]['config_aimants_y'])),BLANC50,angle)
        labels ['t_date'] = ('Date :',(int(guiconfig[self.orientation]['config_l_date_x']),int(guiconfig[self.orientation]['config_l_date_y'])),BLANC50,angle)
        labels ['jj'] = ('01/',(int(guiconfig[self.orientation]['config_d_x']),int(guiconfig[self.orientation]['config_d_y'])),BLANC50,angle)
        labels ['mm'] = ('01/',(int(guiconfig[self.orientation]['config_m_x']),int(guiconfig[self.orientation]['config_m_y'])),BLANC50,angle,)
        labels ['aaaa'] = ('2018',(int(guiconfig[self.orientation]['config_y_x']),int(guiconfig[self.orientation]['config_y_y'])),BLANC50,angle)
        labels ['t_heure'] = ('Heure:',(int(guiconfig[self.orientation]['config_l_heure_x']),int(guiconfig[self.orientation]['config_l_heure_y'])),BLANC50,angle)
        labels ['hh'] = ('00:',(int(guiconfig[self.orientation]['config_hour_x']),int(guiconfig[self.orientation]['config_hour_y'])),BLANC50,angle)
        labels ['min'] = ('00:',(int(guiconfig[self.orientation]['config_minute_x']),int(guiconfig[self.orientation]['config_minute_y'])),BLANC50,angle)
        labels ['ss'] = ('00 ',(int(guiconfig[self.orientation]['config_seconde_x']),int(guiconfig[self.orientation]['config_seconde_y'])),BLANC50,angle,)

        labels ['prec'] = ('<- ',(int(guiconfig[self.orientation]['config_prec_x']),int(guiconfig[self.orientation]['config_prec_y'])),BLANC50,angle,)

        if mode_jour :
            if angle == 0 :
                self.bouton_ok_white = pygame.image.load('./images/ok.jpg')
                self.bouton_ok = pygame.image.load('./images/ok_white.jpg')
            else :
                self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
                self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
            pygame.display.get_surface().fill(BLANC)
        else:
            if angle == 0 :
                self.bouton_ok = pygame.image.load('./images/ok.jpg')
                self.bouton_ok_white = pygame.image.load('./images/ok_white.jpg')
            else :
                self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
                self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
        sprites ['ok'] = (self.bouton_ok,(int(guiconfig[self.orientation]['config_ok_x']),int(guiconfig[self.orientation]['config_ok_y'])))

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.index = 8 # de 0 à 5 : date et heure, 6=precedent, 7=ok, 8=roue, 9=nb aimants
        self.d_roue = int(setupconfig['Parametres']['roue'])
        self.aimants = int(setupconfig['Parametres']['aimants'])

        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])

        if mode_jour :
            if angle == 0 :
                self.bouton_ok_white = pygame.image.load('./images/ok.jpg')
                self.bouton_ok = pygame.image.load('./images/ok_white.jpg')
            else :
                self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
                self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
            pygame.display.get_surface().fill(BLANC)
        else:
            if angle == 0 :
                self.bouton_ok = pygame.image.load('./images/ok.jpg')
                self.bouton_ok_white = pygame.image.load('./images/ok_white.jpg')
            else :
                self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
                self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
            pygame.display.get_surface().fill(NOIR)
        sprites ['ok'] = (self.bouton_ok,(int(guiconfig[self.orientation]['mode_ok_x']),int(guiconfig[self.orientation]['mode_ok_y'])))
        pygame.display.update()
        self.t = time.time()


    def update_time(self):
        # Vérification validité des valeurs
        if self.data[2] < 2018 : self.data[2] = 2018
        if self.data[1] < 1 : self.data[1] = 1
        if self.data[1] > 12 : self.data[1] = 12
        if self.data[0] < 1 : self.data[0] = 1
        if self.data[0] > 31 : self.data[0] = 31
        # Vérification de la validité de la date
        try:
            datetime.datetime(self.data[2],self.data[1],self.data[0])
        except ValueError :
            self.data[0] -= 1
        # Validité de l'heure
        if self.data[3] < 0 : self.data[3] = 0
        if self.data[3] > 23 : self.data[3] = 23
        if self.data[4] < 0 : self.data[4] = 0
        if self.data[4] > 59 : self.data[4] = 59
        if self.data[5] < 0 : self.data[5] = 0
        if self.data[5] > 59 : self.data[5] = 59
        subprocess.Popen ('sudo date "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"'.format(self.data[2],self.data[1],self.data[0],self.data[3],self.data[4],self.data[5]),shell=True)
        subprocess.Popen ('sudo hwclock --set --date "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}" --noadjfile --utc'.format(self.data[2],self.data[1],self.data[0],self.data[3],self.data[4],self.data[5]),shell=True)


    def ProcessInput(self, events, pressed_keys):
        global setupconfig
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                self.t = time.time()
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == BOUTON_RIGHT:
                    self.index+=1
                    if self.index > 9:
                        self.index = 0
                elif event.key == BOUTON_LEFT:
                    self.index -= 1
                    if self.index < 0 :
                        self.index = 9
                elif event.key == BOUTON_DOWN:
                    if self.index < 5 :
                        self.data[self.index] -= 1
                        self.update_time()
                    elif self.index == 5 :
                        self.data[5] = 0
                        self.update_time()
                    elif self.index == 8 :
                        self.d_roue -= 1
                        if self.d_roue < 10 : self.d_roue = 10
                    elif self.index == 9 :
                        self.aimants -= 1
                        if self.aimants < 1 : self.aimants = 1
                elif event.key == BOUTON_UP:
                    if self.index < 5 :
                        self.data[self.index] += 1
                        self.update_time()
                    elif self.index == 5:
                        self.data[5] = 0
                        self.update_time()
                    elif self.index == 8:
                        self.d_roue += 1
                        if self.d_roue > 9999 : self.d_roue = 9999
                    elif self.index == 9 :
                        self.aimants += 1
                        if self.aimants > 20 : self.aimants = 20
                elif event.key == BOUTON_OK:
                    # validation
                    if self.index == 8:
                        setupconfig['Parametres']['roue'] = str(self.d_roue)
                        save_setupconfig()
                    elif self.index == 9:
                        setupconfig['Parametres']['aimants'] = str(self.aimants)
                        save_setupconfig()
                    elif self.index == 6 :
                        self.SwitchToScene(ModeScene())
                    elif self.index == 7 :
                        alphabet = {}
                        alphabet_size_x = {}
                        alphabet_size_y = {}
                        setup_alphabet()
                        self.SwitchToScene(TitleScene())
                    # on passe au réglage suivant, en evitant les boutons prec et ok
                    self.index +=1
                    if self.index > 9:
                        self.index = 0
                    elif self.index == 6 or self.index == 7 :
                        self.index = 8




    def Update(self):
        global labels,old_labels,sprites,old_sprites
        self.now = time.localtime()
        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])
        if self.next == self :
            labels['jj'] = ('{:02d}/'.format(self.data[0]),labels['jj'][1],BLANC50inv,labels['jj'][3]) if self.index == 0 else ('{:02d}/'.format(self.data[0]),labels['jj'][1],BLANC50,labels['jj'][3])
            labels['mm'] = ('{:02d}/'.format(self.data[1]),labels['mm'][1],BLANC50inv,labels['mm'][3]) if self.index == 1 else ('{:02d}/'.format(self.data[1]),labels['mm'][1],BLANC50,labels['mm'][3])
            labels['aaaa'] = ('{:4d}'.format(self.data[2]),labels['aaaa'][1],BLANC50inv,labels['aaaa'][3]) if self.index == 2 else ('{:4d}'.format(self.data[2]),labels['aaaa'][1],BLANC50,labels['aaaa'][3])
            labels['hh'] = ('{:02d}:'.format(self.data[3]),labels['hh'][1],BLANC50inv,labels['hh'][3]) if self.index == 3 else ('{:02d}:'.format(self.data[3]),labels['hh'][1],BLANC50,labels['hh'][3])
            labels['min'] = ('{:02d}:'.format(self.data[4]),labels['min'][1],BLANC50inv,labels['min'][3]) if self.index == 4 else ('{:02d}:'.format(self.data[4]),labels['min'][1],BLANC50,labels['min'][3])
            labels['ss'] = ('{:02d}'.format(self.data[5]),labels['ss'][1],BLANC50inv,labels['ss'][3]) if self.index == 5 else ('{:02d} '.format(self.data[5]),labels['ss'][1],BLANC50,labels['ss'][3])
            labels['roue'] = ('{:4d}mm'.format(self.d_roue),labels['roue'][1],BLANC50inv,labels['roue'][3]) if self.index == 8 else ('{:4d}mm'.format(self.d_roue),labels['roue'][1],BLANC50,labels['roue'][3])
            labels['aimants'] = ('{:2d}  '.format(self.aimants),labels['aimants'][1],BLANC50inv,labels['aimants'][3]) if self.index == 9 else ('{:2d}  '.format(self.aimants),labels['aimants'][1],BLANC50,labels['aimants'][3])

            labels['prec'] = ('<-  ',labels['prec'][1],BLANC50inv,labels['prec'][3]) if self.index == 6 else ('<-  ',labels['prec'][1],BLANC50,labels['prec'][3])
            sprites['ok'] = (self.bouton_ok_white,sprites['ok'][1]) if self.index == 6 else (self.bouton_ok,sprites['ok'][1])

    def Render(self, screen):
        global setupconfig
        update_labels(screen)
        update_sprites(screen)
        k = time.time()
        if k-self.t >= 5:
            save_setupconfig()
            self.SwitchToScene(TitleScene())


#*******************************************************************************************************#
#------------------------- La partie Conversion en Image d'un fichier ----------------------------------#
#*******************************************************************************************************#
class ConversionScene(SceneBase):
    def __init__(self, fname = '',gotoE = False):
        global angle, labels,old_labels,sprites,old_sprites,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname
        self.gotoEdit = gotoE
        self.orientation = setupconfig['Parametres']['orientation']
        self.rallye = rbconfig['Mode']['mode']

        angle = 90 if self.orientation == 'Portrait' else 0

        labels = {}
        old_labels = {}
        image_cache = {}
        myfont = {}
        alphabet = {}
        alphabet_size_x = {}
        alphabet_size_y = {}

        setup_alphabet(VERT25)

        labels ['text'] = ('',(int(guiconfig[self.orientation]['conv_text_x']),int(guiconfig[self.orientation]['conv_text_y'])),VERT25,angle)
        labels ['text1'] = ('',(int(guiconfig[self.orientation]['conv_text1_x']),int(guiconfig[self.orientation]['conv_text1_y'])),VERT25,angle)
        labels ['text2'] = ('',(int(guiconfig[self.orientation]['conv_text2_x']),int(guiconfig[self.orientation]['conv_text2_y'])),VERT25,angle)


    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        pass

    def Render(self, screen):
        global labels,old_labels,sprites,old_sprites,rbconfig
        if mode_jour :
            screen.fill(BLANC)
        else:
            screen.fill(NOIR)
        pygame.display.update()
        labels['text1'] = ('Preparation du roadbook... Patience...',labels['text1'][1],labels['text1'][2],labels['text1'][3])
        filedir = os.path.splitext(self.filename)[0]
        if os.path.isdir('/mnt/piusb/Conversions/'+filedir) == False: # Pas de répertoire d'images, on convertit le fichier
            os.mkdir('/mnt/piusb/Conversions/'+filedir)

			# on vérifie le format de la page :
            width, height = page_size ('/mnt/piusb/'+self.filename)
            if width > height :
                labels['text2'] = ('Conversion des cases en cours...',labels['text2'][1],labels['text2'][2],labels['text2'][3])
                total = page_count ('/mnt/piusb/'+self.filename)
                for i in range (total) :
                    labels['text'] = ('Case {}/{}'.format(i,total),labels['text'][1],labels['text'][2],labels['text'][3])
                    update_labels(screen)
                    self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = total-i, last_page=total-i, dpi=150, singlefile='{:03}'.format(i+1), fmt='jpg')

            else:
                # conversion et découpage des cases
                labels['text2'] = ('Format Tripy. Conversion en cours...',labels['text2'][1],labels['text2'][2],labels['text2'][3])

                nb_pages = page_count ('/mnt/piusb/'+self.filename)
                #Marge supperieur (pix)
                marge_up = 178
                #Hauteur d'une case (pix)
                hauteur = 177
                #Largeur d'une case (mm)
                largeur = 610
                #Milieu de page (mm)
                milieu = 615
                #Nombre de ligne par page
                nb_ligne = 8
                #Nombre de case par page
                nb_cases = nb_ligne * 2
                total = nb_pages * nb_cases

                w = round(largeur)
                h = round(hauteur)

                for i in range (nb_pages) :
                    for j in range (nb_cases):
                        if j < nb_ligne :
                            x = round(0)
                            y = round(marge_up+(nb_ligne-j-1)*hauteur)
                        else :
                            x = round(milieu)
                            y = round(marge_up+(2*nb_ligne-j-1)*hauteur)
                        labels['text'] = ('Case {}/{}'.format(i*nb_cases+j+1,total),labels['text'][1],labels['text'][2],labels['text'][3])
                        self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile='{:03}'.format(i*nb_cases+j),fmt='jpg')
                        update_labels(screen)
            # On se positionne à la premiere case
            rbconfig['Roadbooks']['case'] = '0'
            save_rbconfig()
        else:
            #print('On fait une verification de coherence')
            filedir = os.path.splitext(self.filename)[0]
            nb_pages = page_count ('/mnt/piusb/'+self.filename)
            width, height = page_size ('/mnt/piusb/'+self.filename)
            nb_images = len([f for f in os.listdir('/mnt/piusb/Conversions/'+filedir) if re.search('.jpg$', f)])
            if width > height :
                total = nb_pages
                if total != nb_images :
                    labels['text2'] = ('Pas le meme nombre de cases ! On verifie...', labels['text2'][1],labels['text2'][2],labels['text2'][3])
                    for i in range (total) :
                        labels['text'] = ('Case {}/{}'.format(i,total), labels['text'][1],labels['text'][2],labels['text'][3])
                        self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = total-i, last_page=total-i, dpi=150, singlefile='{:03}'.format(i+1), fmt='jpg')
                        update_labels(screen)
            else :
                # Format Tripy
                #print('Verification coherence Format Tripy')
                nb_ligne = 8
                #Nombre de case par page
                nb_cases = nb_ligne * 2
                total = nb_pages * nb_cases
                nb_images = len([f for f in os.listdir('/mnt/piusb/Conversions/'+filedir) if re.search('.jpg$', f)])
                if total != nb_images :
                    labels['text2'] = ('Pas le meme nombre de cases ! On verifie...', labels['text2'][1],labels['text2'][2],labels['text2'][3])
                    #Marge supperieur (pix)
                    marge_up = 178
                    #Hauteur d'une case (pix)
                    hauteur = 177
                    #Largeur d'une case (mm)
                    largeur = 610
                    #Milieu de page (mm)
                    milieu = 615
                    #Nombre de ligne par page
                    nb_ligne = 8
                    #Nombre de case par page
                    nb_cases = nb_ligne * 2
                    total = nb_pages * nb_cases

                    w = round(largeur)
                    h = round(hauteur)

                    for i in range (nb_pages) :
                        for j in range (nb_cases):
                            if j < nb_ligne :
                                x = round(0)
                                y = round(marge_up+(nb_ligne-j-1)*hauteur)
                            else :
                                x = round(milieu)
                                y = round(marge_up+(2*nb_ligne-j-1)*hauteur)
                            labels['text'] = ('Case {}/{}'.format(i*nb_cases+j+1,total),labels['text'][1],labels['text'][2],labels['text'][3])
                            self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile='{:03}'.format(i*nb_cases+j),fmt='jpg')
                            update_labels(screen)
            if int(rbconfig['Roadbooks']['case']) < 0 or int(rbconfig['Roadbooks']['case']) > total -2 :
              # Pb avec la position sauvegardée. On se positionne au début du rb
              rbconfig['Roadbooks']['case'] = '0'
              save_rbconfig()

        if self.gotoEdit:
            self.SwitchToScene(EditScene(self.filename))
        else :
            if self.rallye == 'Zoom' :
                self.SwitchToScene(RoadbookZoomScene(self.filename))
            else :
                self.SwitchToScene(RoadbookScene(self.filename))

#*******************************************************************************************************#
#---------------------------------------- La partie Annotations de Roadbooks  --------------------------#
#*******************************************************************************************************#
class EditScene(SceneBase):
    def __init__(self, fname = ''):
        global labels,old_labels,sprites,old_sprites,filedir,fichiers,rb_ratio,angle,myfont,alphabet,alphabet_size_x,alphabet_size_y,fps
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname
        filedir = os.path.splitext(self.filename)[0]
        if os.path.isdir('/mnt/piusb/Annotations/'+filedir) == False: # Pas de répertoire d'annotation, on creeme repertoire
            os.mkdir('/mnt/piusb/Annotations/'+filedir)

        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        image_cache = {}

        angle = 0
        fps = 60

        setup_alphabet(BLANC25inv)
        setup_alphabet(BLANC25)

        #Chargement des images
        fichiers = sorted([name for name in os.listdir('/mnt/piusb/Conversions/'+filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+filedir, name))])
        self.nb_cases = len(fichiers)
        samplepage = pygame.image.load (os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[0]))
        (w,h) = samplepage.get_rect().size
        rb_ratio = 800/w
        # Mise à l'échelle des images
        self.nh = h * rb_ratio
        self.case = 0
        self.old_case = -1
        sprites['case'] = (pygame.transform.rotozoom (pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[self.case])),0,rb_ratio),(0,0))

        if mode_jour :
            pygame.display.get_surface().fill(BLANC)
            labels['case'] = ('001/{:03d}'.format(self.nb_cases),(300,430),BLANC25inv,0)
        else :
            pygame.display.get_surface().fill(NOIR)
            labels['case'] = ('001/{:03d}'.format(self.nb_cases),(300,430),BLANC25,0)
        pygame.display.update()


        self.last_coords = (800,480)
        self.canvas = sprites['case'][0].copy()
        self.canvas.fill(BLANC)
        if os.path.isfile('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,self.case)) :
            self.canvas = pygame.image.load ('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,self.case)).convert()
        self.canvas.set_colorkey(BLANC)
        self.mouse = pygame.mouse


    def ProcessInput(self, events, pressed_keys):
        global filedir,fps
        left_pressed, middle_pressed, right_pressed = self.mouse.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            elif event.type == pygame.KEYDOWN :
                pygame.image.save(self.canvas,'/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,self.case))
                if event.key == BOUTON_OK :
                    self.SwitchToScene(TitleScene())
                    fps = 5
                elif event.key == BOUTON_DOWN :
                    self.case += 1
                elif event.key == BOUTON_UP :
                    self.case -= 1
                elif event.key == BOUTON_BACKSPACE :
                    self.canvas = sprites['case'][0].copy()
                    self.canvas.fill(BLANC)
                    pygame.image.save(self.canvas,'/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,self.case))
                elif event.key == BOUTON_LEFT :
                    self.case -= 10
                elif event.key == BOUTON_RIGHT :
                    self.case += 10
                if self.case < 0 : self.case = 0
                if self.case >= self.nb_cases : self = self.nb_cases-1
                # On charge l'ancienne annotation si elle existe
                if os.path.isfile('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,self.case)) :
                    self.canvas = pygame.image.load ('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,self.case)).convert()
                else :
                    self.canvas.fill(BLANC)
                self.canvas.set_colorkey(BLANC)
            elif left_pressed :
                self.c = pygame.mouse.get_pos()
                if self.last_coords == (800,480) : self.last_coords = self.c
                self.coords = self.c
                pygame.draw.line(self.canvas, ROUGE,self.last_coords, self.coords,5)
                self.last_coords = self.coords
            else :
                self.last_coords = (800,480)

    def Update(self):
        if self.next == self :
            if self.old_case != self.case :
                sprites['case'] = (pygame.transform.rotozoom (pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[self.case])),0,rb_ratio),(0,0))
                labels['case'] = ('{:3d}/{:3d}'.format(self.case+1,self.nb_cases),labels['case'][1],labels['case'][2],labels['case'][3])
                self.old_case = self.case


    def Render(self, screen):
        global sprites
        if mode_jour :
            screen.fill(BLANC)
        else :
            screen.fill(NOIR)
        for i in list(labels.keys()) :
            blit_text (screen,labels[i][0],labels[i][1],labels[i][2],labels[i][3])
        for i in list(sprites.keys()) :
            screen.blit (sprites[i][0],sprites[i][1])
        screen.blit (self.canvas,(0,0))
        pygame.display.flip()


#*******************************************************************************************************#
#------------------------- La partie Dérouleur ---------------------------------------------------------#
#*******************************************************************************************************#
class RoadbookScene(SceneBase):
    def __init__(self, fname = ''):
        global developpe,roue,aimants, distance1,old_distance1,save_t_moy,save_t_odo,totalisateur,speed,vmoy,vmax,image_cache,filedir,fichiers,rb_ratio,labels, old_labels,sprites, old_sprites,angle,myfont,alphabet,alphabet_size_x,alphabet_size_y
        global widgets,current_widget,old_widget
        SceneBase.__init__(self,fname)
        filedir = os.path.splitext(self.filename)[0]
        check_configfile()
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        image_cache = {}
        #widgets = {}

        temps1 = time.time()-chrono_time1

        if chrono_time1 == 0 :
            vmoy = 0
        else:
            vmoy = distance/temps1*3.6/1000
        vmax = 0
        speed = 0

        self.orientation = setupconfig['Parametres']['orientation']
        angle = 90 if self.orientation == 'Portrait' else 0

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.pages = {}

        roue = int(setupconfig['Parametres']['roue'])
        aimants = int(setupconfig['Parametres']['aimants'])
        developpe = 1.0*roue / aimants

        old_distance1 = distance1

        #Chargement des images
        fichiers = sorted([name for name in os.listdir('/mnt/piusb/Conversions/'+filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+filedir, name))])
        self.nb_cases = len(fichiers)
        self.case = int(rbconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = 0 # on compte de 0 à longueur-1
        self.oldcase = self.case + 1

        samplepage = pygame.image.load (os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[0]))
        (w,h) = samplepage.get_rect().size
        rb_ratio = min(480/w,150/h) if self.orientation == 'Portrait' else min(500/w,160/h)
        # Mise à l'échelle des images
        self.nh = h * rb_ratio

        if mode_jour :
            pygame.display.get_surface().fill(BLANC)
        else :
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()

        save_t_moy = time.time()
        save_t_odo = time.time()
        current_widget = 0
        old_widget = 0

    def ProcessInput(self, events, pressed_keys):
        global distance1,old_distance1,vmoy,vmax,save_t_moy,save_t_odo,chrono_delay1
        global widgets,current_widget,nb_widgets
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()

                # les actions sur le widget courant
                elif event.key == BOUTON_RIGHT:
                    widgets[(current_widget)].down()
                elif event.key == BOUTON_LEFT:
                    widgets[(current_widget)].up()
                elif event.key == BOUTON_OK:
                    widgets[(current_widget)].deselect()
                    current_widget += 1
                    if current_widget > nb_widgets :
                        current_widget = 0
                    widgets[(current_widget)].select()
                elif event.key == BOUTON_BACKSPACE:
                    widgets[(current_widget)].reset()
                elif event.key == BOUTON_HOME:
                    widgets[(current_widget)].upup()
                elif event.key == BOUTON_END:
                    widgets[(current_widget)].downdown()
                # les actions de deroulement du rb
                elif event.key == BOUTON_UP:
                    self.oldcase = self.case
                    self.case -= 1
                elif event.key == BOUTON_PGUP:
                        self.case = 0
                elif event.key == BOUTON_DOWN:
                    self.oldcase = self.case
                    self.case += 1
                elif event.key == BOUTON_PGDOWN:
                    self.case = self.nb_cases - ncases

        # Action sur le dérouleur
        if self.case > self.nb_cases - ncases :
            self.case = self.nb_cases - ncases
        if self.case < 0 :
            self.case = 0

    def Update(self):
        global save_t_odo,angle,totalisateur,distance1,distance2
        global sprites,old_sprites,rbconfig,chronoconfig,odoconfig
        global chrono_delay1,chrono_time1,chrono_delay2,chrono_time2
        global widgets,force_refresh

        # MAJ des cases du rb
        if (self.case != self.oldcase) or force_refresh :
            # On sauvegarde la nouvelle position
            rbconfig['Roadbooks']['case'] = str(self.case)
            save_rbconfig()
            if angle == 0 :
                for n in range(ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle,mode_jour),(0,480-(n+1)*self.nh-n))
            else :
                for n in range(ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle,mode_jour),(800-(n+1)*self.nh-n,0))
            self.oldcase=self.case

        # MAJ des infos des widgets
        for j in list(widgets.keys()):
            widgets[j].update()

        # Sauvegarde de l'odometre, distances et temps de depart de chrono toutes les 5 secondes
        k = time.time()
        if k - save_t_odo >= 5 : # On sauvegarde l'odometre toutes les 5 secondes
            odoconfig['Odometre']['Totalisateur'] = str(totalisateur)
            odoconfig['Odometre']['Distance1'] = str(distance1)
            odoconfig['Odometre']['Distance2'] = str(distance2)
            save_odoconfig()
            save_t_odo = time.time()
            chronoconfig['Chronometre1']['chrono_delay'] = str(chrono_delay1)
            chronoconfig['Chronometre1']['chrono_time'] = str(chrono_time1)
            chronoconfig['Chronometre2']['chrono_delay'] = str(chrono_delay2)
            chronoconfig['Chronometre2']['chrono_time'] = str(chrono_time2)
            save_chronoconfig()


    def Render(self, screen):
        global widgets,current_widget,old_widget
        # Positionnement des différents éléments d'affichage, s'ils ont été modifiés
        update_sprites(screen)
        for j in list(widgets.keys()):
            widgets[j].render(screen)
        #update_labels(screen)



#*******************************************************************************************************#
#---------------------------------------- Ecran Compteur de vitesse simple -----------------------------#
#*******************************************************************************************************#

class OdometerScene(SceneBase):
    def __init__(self, fname = ''):
        global roue, aimants,developpe, distance1,distance2,old_distance1,old_distance2,totalisateur,speed,save_t_moy, save_t_odo,labels, old_labels,angle,myfont,alphabet,alphabet_size_x,alphabet_size_y
        global widgets, current_screen,old_screen
        SceneBase.__init__(self,fname)
        widgets = {}
        check_configfile()

        temps1 = time.time()-chrono_time1

        if chrono_time1 == 0 :
            vmoy = 0
        else:
            vmoy = distance/temps1*3.6/1000
        vmax = 0
        speed = 0

        self.orientation = setupconfig['Parametres']['orientation']
        angle = 90 if self.orientation == 'Portrait' else 0

        self.index = 0 # totalisateur par defaut

        roue = int(setupconfig['Parametres']['roue'])
        aimants = int(setupconfig['Parametres']['aimants'])
        developpe = 1.0*roue / aimants

        old_distance1 = distance1
        old_distance2 = distance2

        if mode_jour:
            pygame.display.get_surface().fill(BLANC)
        else:
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()

        save_t_moy = time.time()
        save_t_odo = time.time()
        current_screen = 1
        old_widget = 1

    def ProcessInput(self, events, pressed_keys):
        global distance1,old_distance1,vmoy,vmax,save_t_moy,save_t_odo,chrono_delay1
        global widgets,current_screen,screenconfig,nb_widgets
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                # les actions sur le widget courant
                elif event.key == BOUTON_OK:
                    widgets[(0)].reset()
                elif event.key == BOUTON_BACKSPACE:
                    widgets[(1)].reset()

    def Update(self):
        global save_t_odo,angle,totalisateur,distance1,distance2
        global chronoconfig,odoconfig
        global chrono_delay1,chrono_time1,chrono_delay2,chrono_time2
        global widgets

        # MAJ des infos des widgets
        for j in list(widgets.keys()):
            widgets[j].update()

        # Sauvegarde de l'odometre, distances et temps de depart de chrono toutes les 5 secondes
        k = time.time()
        if k - save_t_odo >= 5 : # On sauvegarde l'odometre toutes les 5 secondes
            odoconfig['Odometre']['Totalisateur'] = str(totalisateur)
            odoconfig['Odometre']['Distance1'] = str(distance1)
            odoconfig['Odometre']['Distance2'] = str(distance2)
            save_odoconfig()
            save_t_odo = time.time()
            chronoconfig['Chronometre1']['chrono_delay'] = str(chrono_delay1)
            chronoconfig['Chronometre1']['chrono_time'] = str(chrono_time1)
            chronoconfig['Chronometre2']['chrono_delay'] = str(chrono_delay2)
            chronoconfig['Chronometre2']['chrono_time'] = str(chrono_time2)
            save_chronoconfig()

    def Render(self, screen):
        global widgets
        # Positionnement des différents éléments d'affichage, s'ils ont été modifiés
        for j in list(widgets.keys()):
            widgets[j].render(screen)

#*******************************************************************************************************#
#------------------------- La partie Derouleur Zoom   --------------------------------------------------#
#*******************************************************************************************************#
class RoadbookZoomScene(SceneBase):
    def __init__(self, fname = ''):
        global image_cache,filedir,fichiers,rb_ratio,sprites, old_sprites,angle
        SceneBase.__init__(self,fname)
        filedir = os.path.splitext(self.filename)[0]
        check_configfile()
        sprites = {}
        old_sprites = {}
        image_cache = {}

        self.orientation = setupconfig['Parametres']['orientation']
        angle = 90 if self.orientation == 'Portrait' else 0
        self.ncases = 6 if self.orientation == 'Portrait' else 2

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.pages = {}

        #Chargement des images
        fichiers = sorted([name for name in os.listdir('/mnt/piusb/Conversions/'+filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+filedir, name))])
        self.nb_cases = len(fichiers)
        self.case = int(rbconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = 0 # on compte de 0 à longueur-1
        self.oldcase = self.case + 1

        samplepage = pygame.image.load (os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[0]))
        (w,h) = samplepage.get_rect().size
        rb_ratio = 480/w if self.orientation == 'Portrait' else 800/w
        # Mise à l'échelle des images
        self.nh = h * rb_ratio

        if mode_jour :
            pygame.display.get_surface().fill(BLANC)
        else :
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == BOUTON_UP:
                    self.oldcase = self.case
                    self.case -= 1
                elif event.key == BOUTON_PGUP:
                        self.case = 0
                elif event.key == BOUTON_DOWN:
                    self.oldcase = self.case
                    self.case += 1
                elif event.key == BOUTON_PGDOWN:
                    self.case = self.nb_cases - self.ncases

        # Action sur le dérouleur
        if self.case > self.nb_cases - self.ncases :
            self.case = self.nb_cases -self.ncases
        if self.case < 0 :
            self.case = 0

    def Update(self):
        global sprites,old_sprites,rbconfig,mode_jour
        if self.case != self.oldcase :
            # On sauvegarde la nouvelle position
            rbconfig['Roadbooks']['case'] = str(self.case)
            save_rbconfig()
            if angle == 0 :
                for n in range(self.ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle,mode_jour),(0,480-(n+1)*self.nh))
            else :
                for n in range(self.ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle,mode_jour),(800-(n+1)*self.nh,0))
            self.oldcase = self.case

    def Render(self, screen):
        # Positionnement des différents éléments d'affichage, s'ils ont été modifiés
        update_sprites(screen)

#*******************************************************************************************************#
#------------------------- Definition des routes Flask   -----------------------------------------------#
#*******************************************************************************************************#
#@app.route('/')
#def index():

#    return render_template('rallye.html')


# Pour optimisation
#import cProfile
#cProfile.run ('run_RpiRoadbook(800, 480, 60, TitleScene())')

#if __name__ == '__main__':
#    socketio.run(app,host='0.0.0.0')
run_RpiRoadbook(800, 480, TitleScene())
