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

import sys
os.environ["SDL_FBDEV"] = "/dev/fb0"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = "/dev/input/event0"

fps = 5

totalisateur = 0
distance = 0
distancetmp = 0
distance2 = 0
speed = 0.00
roue = 1864
aimants = 1
developpe = 1864
vmax = 0.00
vmoy = 0.0
tps = 0.0
tpsinit=0.0
cmavant = 0
cmavant2 = 0
j = time.time()
temperature = -1
cpu = -1

filedir = ''
fichiers = []

rb_ratio = 1
rb_ration_annot = 1

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
GMASSSTORAGE    = USEREVENT+1 # Event branchement en mode cle usb
USB_DISCONNECTED = USEREVENT+2 # Event Cable usb debranche

GPIO_ROUE = 17
GPIO_LEFT = 27
GPIO_RIGHT = 22
GPIO_OK = 23
GPIO_UP = 24
GPIO_DOWN = 25

GPIO_DIM = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_ROUE, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Capteur de vitesse
GPIO.setup(GPIO_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_DIM, GPIO.OUT)
pulse = GPIO.PWM(GPIO_DIM,800) # fréquence de 800Hz
pulse.start(100.0)

# Test bouton au démarrage pour menu de configuration
gotoConfig = not GPIO.input(GPIO_OK)

#*******************************************************************************************************#
#------------------------- Les callbacks des interruptions GPIO et fonctions utiles --------------------#
#*******************************************************************************************************#
def input_roue_callback(channel):
    global totalisateur,distance,distancetmp
    totalisateur += developpe
    distance += developpe
    distancetmp += developpe
    distance2 += developpe

def input_left_callback(channel):
    GPIO.remove_event_detect(channel)
    b4_time = time.time()
    time.sleep(.2)
    while not GPIO.input(channel) :# on attend le retour du bouton
        time.sleep(.2)
    bouton_time = time.time() - b4_time
    if bouton_time >= 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_HOME}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_LEFT}))
    GPIO.add_event_detect(channel,GPIO.FALLING,callback=input_left_callback,bouncetime=300)


def input_right_callback(channel):
    GPIO.remove_event_detect(channel)
    b4_time = time.time()
    time.sleep(.2)
    while not GPIO.input(channel) :# on attend le retour du bouton
        time.sleep(.2)
    bouton_time = time.time() - b4_time
    if bouton_time >= 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_END}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_RIGHT}))
    GPIO.add_event_detect(channel,GPIO.FALLING,callback=input_right_callback,bouncetime=300)


def input_ok_callback(channel):
    GPIO.remove_event_detect(channel)
    b4_time = time.time()
    time.sleep(.2)
    while not GPIO.input(channel) :# on attend le retour du bouton
        time.sleep(.2)
    bouton_time = time.time() - b4_time
    if bouton_time >= 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_BACKSPACE}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_OK}))
    try :
        GPIO.add_event_detect(channel,GPIO.FALLING,callback=input_ok_callback,bouncetime=300)
    except :
        pass


def input_up_callback(channel):
    GPIO.remove_event_detect(channel)
    b4_time = time.time()
    time.sleep(.2)
    while not GPIO.input(channel) :# on attend le retour du bouton
        time.sleep(.2)
    bouton_time = time.time() - b4_time
    if bouton_time >= 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGUP}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_UP}))
    GPIO.add_event_detect(channel,GPIO.FALLING,callback=input_up_callback,bouncetime=300)


def input_down_callback(channel):
    GPIO.remove_event_detect(channel)
    b4_time = time.time()
    time.sleep(.2)
    while not GPIO.input(channel) :# on attend le retour du bouton
        time.sleep(.2)
    bouton_time = time.time() - b4_time
    if bouton_time >= 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGDOWN}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_DOWN}))
    GPIO.add_event_detect(channel,GPIO.FALLING,callback=input_down_callback,bouncetime=300)


#On définit les interruptions sur les GPIO des commandes
GPIO.add_event_detect(GPIO_ROUE, GPIO.FALLING, callback=input_roue_callback,bouncetime=15)
GPIO.add_event_detect(GPIO_LEFT, GPIO.FALLING, callback=input_left_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_RIGHT, GPIO.FALLING, callback=input_right_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_OK, GPIO.FALLING, callback=input_ok_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_UP, GPIO.FALLING, callback=input_up_callback, bouncetime=300)
GPIO.add_event_detect(GPIO_DOWN, GPIO.FALLING, callback=input_down_callback, bouncetime=300)

#*******************************************************************************************************#
#------------------------- Le callback de la connexion USB ---------------------------------------------#
#*******************************************************************************************************#

def g_mass_storage_callback():
    try:
        rfile = open('/sys/class/udc/20980000.usb/state')
        r = rfile.read()
        if r == 'configured\n' :
             pygame.event.post(pygame.event.Event(GMASSSTORAGE))
        else:
             pygame.event.post(pygame.event.Event(USB_DISCONNECTED))
        rfile.close()
    except:
        pass



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
def get_image(key,angle=0):
    global filedir,fichiers,image_cache
    # Chargement des images uniquement si pas encore en cache
    if not (key,angle) in image_cache:
        img = pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[key]))
        if os.path.isfile('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,key)) : 
            annot = pygame.image.load('/mnt/piusb/Annotations/{}/annotation_{:03d}.png'.format(filedir,key)).convert()
            annot = pygame.transform.rotozoom(annot,0,rb_ratio_annot)
            annot.set_colorkey(BLANC)
            img.blit(annot,(0,0))
        image_cache[(key,angle)] = pygame.transform.rotozoom (img,angle,rb_ratio)
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
#Taille des polices pour chaque style
SALPHA = {BLANC25:25,BLANC50:50,BLANC75:75,BLANC100:100,BLANC200:200,BLANC25inv:25,BLANC50inv:50,ROUGE25:25,ROUGE25inv:25,VERT25:25,GRIS75:75}

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
    fg_jour = { BLANC25:NOIR,  BLANC50:NOIR,  BLANC75:NOIR,  BLANC100:NOIR,  BLANC200:NOIR,  BLANC25inv:BLANC, BLANC50inv:BLANC, ROUGE25:ROUGE, ROUGE25inv:BLANC, VERT25:BLEU,  GRIS75:GRIS}
    bg_jour = { BLANC25:BLANC, BLANC50:BLANC, BLANC75:BLANC, BLANC100:BLANC, BLANC200:BLANC, BLANC25inv:NOIR,  BLANC50inv:NOIR,  ROUGE25:BLANC, ROUGE25inv:ROUGE, VERT25:BLANC, GRIS75:BLANC}
    fg_nuit = { BLANC25:BLANC, BLANC50:BLANC, BLANC75:BLANC, BLANC100:BLANC, BLANC200:BLANC, BLANC25inv:NOIR,  BLANC50inv:NOIR,  ROUGE25:ROUGE, ROUGE25inv:ROUGE,  VERT25:VERT,  GRIS75:GRIS}
    bg_nuit = { BLANC25:NOIR,  BLANC50:NOIR,  BLANC75:NOIR,  BLANC100:NOIR,  BLANC200:NOIR,  BLANC25inv:BLANC, BLANC50inv:BLANC, ROUGE25:NOIR,  ROUGE25inv:BLANC, VERT25:NOIR,  GRIS75:NOIR}

    if mode_jour :
        if angle == 90 :
            for i in printable :
                alphabet[(i,police,angle)] = pygame.transform.rotate (myfont[police].render(i,0,fg_jour[police],bg_jour[police]),90)
                alphabet_size_x[(i,police,angle)] = 0 
                alphabet_size_y[(i,police,angle)] = -alphabet[(i,police,angle)].get_size()[1]    
        else :
            for i in printable :
                alphabet[(i,police,angle)] = myfont[police].render(i,0,fg_jour[police],bg_jour[police])
                alphabet_size_x[(i,police,angle)] = alphabet[(i,police,angle)].get_size()[0]
                alphabet_size_y[(i,police,angle)] = 0
    else :
        if angle == 90 :
            for i in printable :
                alphabet[(i,police,angle)] = pygame.transform.rotate (myfont[police].render(i,0,fg_nuit[police],bg_nuit[police]),90)
                alphabet_size_x[(i,police,angle)] = 0 
                alphabet_size_y[(i,police,angle)] = -alphabet[(i,police,angle)].get_size()[1]    
        else :
            for i in printable :
                alphabet[(i,police,angle)] = myfont[police].render(i,0,fg_nuit[police],bg_nuit[police])
                alphabet_size_x[(i,police,angle)] = alphabet[(i,police,angle)].get_size()[0]
                alphabet_size_y[(i,police,angle)] = 0
            

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
            if (i in old_labels.keys()) and (len(old_labels[i]) < len (labels[i])) :
                 blit_text (screen,' '*len(old_labels[i]),old_labels[i][1],old_labels[i][2],old_labels[i][3])
            blit_text (screen,labels[i][0],labels[i][1],labels[i][2],labels[i][3])
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
    global sprites,old_sprites
    for i in list(sprites.keys()) :
        if (i not in old_sprites.keys()) or (old_sprites [i] != sprites[i]) :
            blit_sprite (screen,sprites[i][0],sprites[i][1])
            old_sprites [i] = sprites[i]

#----------------------------------------------------------------------------------------------#
#-------------------------- Vérification configfiles ------------------------------------------#
#----------------------------------------------------------------------------------------------#
setupconfig = configparser.ConfigParser()
guiconfig = configparser.ConfigParser()
rbconfig = configparser.ConfigParser()

def save_setupconfig():
    global setupconfig
    for attempt in range(5):
        try :
            with open('/mnt/piusb/.conf/RpiRoadbook_setup.cfg', 'w') as configfile:
                setupconfig.write(configfile)
        except :
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
            time.sleep(.2)
        else : 
            break
    else :
        print('Write Error RpiRoadbook.cfg after 5 tries')

def check_configfile():
    global guiconfig,setupconfig,mode_jour,rbconfig
    # On charge les emplacements des elements d'affichage
    guiconfig.read('/home/rpi/RpiRoadbook/gui.cfg')

    # On charge les reglages : mode, orientation, etc
    candidates = ['/home/rpi/RpiRoadbook/default.cfg','/mnt/piusb/.conf/RpiRoadbook_setup.cfg']
    setupconfig.read(candidates)
    save_setupconfig()

    mode_jour = setupconfig['Parametres']['jour_nuit'] == 'Jour'

    # On charge le roadbook en cours et sa case
    candidates = ['/home/rpi/RpiRoadbook/RpiRoadbook.cfg','/mnt/piusb/.conf/RpiRoadbook.cfg']
    rbconfig.read(candidates)
    save_rbconfig()



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
    t_usb = time.time()
    check_configfile()

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        # On ne checke la connectivité usb, la température et la charge cpu que toutes les 5 secondes
        if time.time() - 5 > t_usb : 
            g_mass_storage_callback()
            t_usb = time.time()   
            rpi_temp()    
            cpu_load()

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
            elif event.type == GMASSSTORAGE:
                active_scene.SwitchToScene(G_MassStorageScene())

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
            self.rallye = setupconfig['Parametres']['mode']
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
                    self.column -= 1
                    if self.column < 1 : self.column = 2
                elif event.key == BOUTON_RIGHT :
                    self.iscountdown = False
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
            elif event.type == GMASSSTORAGE :
                self.iscountdown = False
                self.SwitchToScene(G_MassStorageScene())

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
        labels['text3'] = ('au menu apres telechargement', (100,260),ROUGE25,0)

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            elif event.type == pygame.KEYDOWN :
                if event.key == BOUTON_LEFT or event.key == BOUTON_RIGHT or event.key == BOUTON_OK or event.key == BOUTON_UP or event.key == BOUTON_DOWN :
                    self.SwitchToScene(TitleScene())
            elif event.type == GMASSSTORAGE:
                self.SwitchToScene(G_MassStorageScene())

    def Update(self):
        pass

    def Render(self, screen):
        update_labels(screen)

#*******************************************************************************************************#
#---------------------------------------- La partie Mode -----------------------------------------------#
#*******************************************************************************************************#
class ModeScene(SceneBase):
    def __init__(self, fname = ''):
        global setupconfig,angle,labels,old_labels,sprites,old_sprites, mode_jour,myfont,alphabet,alphabet_size_x,alphabet_size_y
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
        labels ['t_dim'] = ('Luminosite :',(int(guiconfig[self.orientation]['mode_l_dim_x']),int(guiconfig[self.orientation]['mode_l_dim_y'])),BLANC50,angle)
        labels ['dim'] = ('100',(int(guiconfig[self.orientation]['mode_dim_x']),int(guiconfig[self.orientation]['mode_dim_y'])),BLANC50,angle)
        labels ['t_orientation'] = ('Orientation :',(int(guiconfig[self.orientation]['mode_l_orientation_x']),int(guiconfig[self.orientation]['mode_l_orientation_y'])),BLANC50,angle)
        labels ['orientation'] = ('Portrait ',(int(guiconfig[self.orientation]['mode_orientation_x']),int(guiconfig[self.orientation]['mode_orientation_y'])),BLANC50,angle)
        
        labels ['suivant'] = ('->',(int(guiconfig[self.orientation]['mode_suiv_x']),int(guiconfig[self.orientation]['mode_suiv_y'])),BLANC50,angle)

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.index = 0 # 0= mode, 1=nuit, 2=luminosite, 3=orientation, 4=suivant, 5 = ok

        self.rallye = setupconfig['Parametres']['mode']
        mode_jour = setupconfig['Parametres']['jour_nuit'] == 'Jour'
        self.dim = int(setupconfig['Parametres']['luminosite'])
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
        global setupconfig,mode_jour,alphabet,alphabet_size_x,alphabet_size_y,old_labels, old_sprites
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
                        setupconfig['Parametres']['mode'] = self.rallye 
                        save_setupconfig()

                    elif self.index == 1 :
                        mode_jour = not mode_jour
                        setupconfig['Parametres']['jour_nuit'] = 'Jour' if mode_jour else 'Nuit'
                        save_setupconfig()

                    elif self.index == 2 :
                        self.dim -= 5
                        if self.dim < 5 : self.dim = 5
                        pulse.ChangeDutyCycle(self.dim)
                        setupconfig['Parametres']['luminosite'] = str(self.dim)
                        save_setupconfig()

                    elif self.index == 3 :
                        self.paysage = not self.paysage
                        setupconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        subprocess.Popen('sudo ./paysage.sh',shell=True) if self.paysage else subprocess.Popen('sudo ./portrait.sh',shell=True)
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
                        self.dim += 5
                        if self.dim > 100 : self.dim = 100
                        pulse.ChangeDutyCycle(self.dim)
                    elif self.index == 3 :
                        self.paysage = not self.paysage
                        setupconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        subprocess.Popen('sudo ./paysage.sh',shell=True) if self.paysage else subprocess.Popen('sudo ./portrait.sh',shell=True)
                        save_setupconfig()

                elif event.key == BOUTON_OK:
                    # validation
                    if self.index == 0:
                        setupconfig['Parametres']['mode'] = self.rallye
                        save_setupconfig()
                    elif self.index == 1:
                        setupconfig['Parametres']['jour_nuit'] = 'Jour' if mode_jour else 'Nuit'
                        save_setupconfig()
                    elif self.index == 2 :
                        setupconfig['Parametres']['luminosite'] = str(self.dim)
                        save_setupconfig()
                    elif self.index == 3:
                        setupconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        subprocess.Popen('sudo ./paysage.sh',shell=True) if self.paysage else subprocess.Popen('sudo ./portrait.sh',shell=True)
                        save_setupconfig()       
                    elif self.index == 4 : 
                        self.SwitchToScene(ConfigScene())
                    elif self.index == 5 : 
                        alphabet = {}
                        alphabet_size_x = {}
                        alphabet_size_y = {}
                        setup_alphabet()
                        self.SwitchToScene(TitleScene())
                    # on passe au réglage suivant
                    self.index +=1
                    if self.index > 3:
                        self.index = 0        

    def Update(self):
        global labels,old_labels,sprites,old_sprites
        if self.next == self :
            labels['mode'] = (self.rallye,labels['mode'][1],BLANC50inv,labels['mode'][3]) if self.index == 0 else (self.rallye,labels['mode'][1],BLANC50,labels['mode'][3])

            if mode_jour :
                labels['jour_nuit'] = ('Jour   ',labels['jour_nuit'][1],BLANC50inv,labels['jour_nuit'][3]) if self.index == 1 else ('Jour   ',labels['jour_nuit'][1],BLANC50,labels['jour_nuit'][3])
            else :
                labels['jour_nuit'] = ('Nuit   ',labels['jour_nuit'][1],BLANC50inv,labels['jour_nuit'][3]) if self.index == 1 else ('Nuit   ',labels['jour_nuit'][1],BLANC50,labels['jour_nuit'][3])

            labels['dim'] = ('{:3d}%'.format(self.dim),labels['dim'][1],BLANC50inv,labels['dim'][3]) if self.index == 2 else ('{:3d}%'.format(self.dim),labels['dim'][1],BLANC50,labels['dim'][3])

            if self.paysage :
                labels['orientation'] = ('Paysage',labels['orientation'][1],BLANC50inv,labels['orientation'][3]) if self.index == 3 else ('Paysage ',labels['orientation'][1],BLANC50,labels['orientation'][3])
            else :
                labels['orientation'] = ('Portrait ',labels['orientation'][1],BLANC50inv,labels['orientation'][3]) if self.index == 3 else ('Portrait ',labels['orientation'][1],BLANC50,labels['orientation'][3])

            labels ['suivant'] = ('->',labels['suivant'][1],BLANC50inv,labels['suivant'][3]) if self.index == 4 else ('->',labels['suivant'][1],BLANC50,labels['suivant'][3])
            sprites['ok'] = (self.bouton_ok_white,sprites['ok'][1]) if self.index == 5 else (self.bouton_ok,sprites['ok'][1])

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
#---------------------------------------- La partie Gadget Mass Storage --------------------------------#
#*******************************************************************************************************#
class G_MassStorageScene(SceneBase):
    def __init__(self, fname = ''):
        global labels,old_labels,sprites,old_sprites,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        pygame.font.init()
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        
        setup_alphabet(ROUGE25)
        sprites['usb'] = (pygame.image.load ('./images/usb_connected_white.jpg'),(0,0))
        labels ['text'] = ('Appuyez sur un bouton une fois le cable debranche pour retourner au menu',(10,450),ROUGE25,0)
        #os.system('umount /mnt/piusb')

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == BOUTON_LEFT or event.key == BOUTON_RIGHT or event.key == BOUTON_OK or event.key == BOUTON_UP or event.key == BOUTON_DOWN :
                    #os.system('modprobe -r g_mass_storage')
                    #time.sleep(1)
                    #os.system('modprobe g_mass_storage file=/home/rpi/piusb.bin stall=0 ro=0 removable=1')
                    #time.sleep(1)
                    #os.system('mount -t vfat /home/rpi/piusb.bin /mnt/piusb')
                    #time.sleep(1)
                    self.SwitchToScene(TitleScene())
        

    def Update(self):
        pass

    def Render(self, screen):
        update_labels(screen)
        update_sprites(screen)



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
        self.rallye = setupconfig['Parametres']['mode']

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
            # On se positionne à l'avant dernière case (ou la 2ème dans l'ordre de lecteur du rb
            rbconfig['Roadbooks']['case'] = str(total-2)
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
                if self.last_coords != (800,480) :
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
        global developpe,roue,aimants, distance,cmavant,distancetmp,totalisateur,speed,vmoy,vmax,image_cache,filedir,fichiers,rb_ratio,rb_ratio_annot,labels, old_labels,sprites, old_sprites,angle,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self,fname)
        filedir = os.path.splitext(self.filename)[0]
        check_configfile()
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        image_cache = {}
        
        vmoy = 0
        vmax = 0
        speed = 0

        self.orientation = setupconfig['Parametres']['orientation']
        angle = 90 if self.orientation == 'Portrait' else 0

        setup_alphabet(BLANC75)
        setup_alphabet(BLANC100)
        setup_alphabet(ROUGE25)
        setup_alphabet(GRIS75)

        # Dans l'ordre : heure,odometre,texte_vitesse,vitesse,texte_vitessemoyenne,vitessemoyenne,
        labels['heure'] = ('00:00:00',(int(guiconfig[self.orientation]['rb_tps_x']),int(guiconfig[self.orientation]['rb_tps_y'])),BLANC75,angle)
        labels['distance'] = ('{:6.2f}'.format(0.0),(int(guiconfig[self.orientation]['rb_km_x']),int(guiconfig[self.orientation]['rb_km_y'])),BLANC100,angle)
        labels['t_vitesse'] = ('Vitesse',(int(guiconfig[self.orientation]['rb_t_vi_x']),int(guiconfig[self.orientation]['rb_t_vi_y'])),ROUGE25,angle)
        labels['vitesse'] = ('{:3.0f} '.format(0.0),(int(guiconfig[self.orientation]['rb_vi_x']),int(guiconfig[self.orientation]['rb_vi_y'])),BLANC75,angle)
        labels['t_vmoy'] = ('Vit. moy.',(int(guiconfig[self.orientation]['rb_t_vm_x']),int(guiconfig[self.orientation]['rb_t_vm_y'])),ROUGE25,angle)
        labels['vmoy'] = ('{:3.0f} '.format(0.0),(int(guiconfig[self.orientation]['rb_vm_x']),int(guiconfig[self.orientation]['rb_vm_y'])),GRIS75,angle)
        labels['temperature'] = ('{:4.1f}C'.format(0.0),(int(guiconfig[self.orientation]['rb_temp_x']),int(guiconfig[self.orientation]['rb_temp_y'])),ROUGE25,angle)
        labels['cpu'] = ('{:4.1f}%'.format(0.0),(int(guiconfig[self.orientation]['rb_cpu_x']),int(guiconfig[self.orientation]['rb_cpu_y'])),ROUGE25,angle)
        
        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.ncases = int(guiconfig[self.orientation]['ncases'])
        self.pages = {}

        roue = int(setupconfig['Parametres']['roue'])
        aimants = int(setupconfig['Parametres']['aimants'])
        developpe = 1.0*roue / aimants

        import logging
        from logging.handlers import RotatingFileHandler

        try :
            with open('/mnt/piusb/.log/odometre.log', "r") as f1:
                last_line = f1.readlines()[-1]
                distance = int(last_line)
        except :
            distance = 0
        cmavant = distance
        distancetmp=0

        self.odometre_log = logging.getLogger('Rotating Odometer Log')
        self.odometre_log.setLevel(logging.INFO)
        self.odometre_handler = RotatingFileHandler('/mnt/piusb/.log/odometre.log',maxBytes=8000,backupCount=20)
        self.odometre_log.addHandler(self.odometre_handler)

        try :
            with open('/mnt/piusb/.log/totalisateur.log', "r") as f2:
                last_line = f2.readlines()[-1]
                totalisateur = int(last_line)
        except :
            totalisateur = 0

        self.totalisateur_log = logging.getLogger('Rotating Totalisateur Log')
        self.totalisateur_log.setLevel(logging.INFO)
        self.totalisateur_handler = RotatingFileHandler('/mnt/piusb/.log/totalisateur.log',maxBytes=8000,backupCount=20)
        self.totalisateur_log.addHandler(self.totalisateur_handler)

        #Chargement des images
        fichiers = sorted([name for name in os.listdir('/mnt/piusb/Conversions/'+filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+filedir, name))])
        self.nb_cases = len(fichiers)
        self.case = int(rbconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = 0 # on compte de 0 à longueur-1
        self.oldcase = self.case + 1
        
        samplepage = pygame.image.load (os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[0]))
        (w,h) = samplepage.get_rect().size
        rb_ratio = min(480/w,150/h) if self.orientation == 'Portrait' else min(600/w,180/h)
        rb_ratio_annot = 480/w if self.orientation == 'Portrait' else 600/800
        # Mise à l'échelle des images
        self.nh = h * rb_ratio

        if mode_jour :
            pygame.display.get_surface().fill(BLANC)
        else :
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()

        j = time.time()

    def ProcessInput(self, events, pressed_keys):
        global distance,tpsinit,cmavant,vmoy,vmax,distancetmp
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == BOUTON_RIGHT:
                    distance+=10000
                    cmavant=distance
                elif event.key == BOUTON_END:
                    distance+=50000
                    cmavant=distance
                elif event.key == BOUTON_LEFT:
                    distance-=10000
                    if distance <= 0 : distance = 0
                    cmavant = distance
                elif event.key == BOUTON_HOME:
                    distance-=50000
                    if distance <= 0 : distance = 0
                    cmavant = distance
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
                elif event.key == BOUTON_BACKSPACE:
                    distance = 0
                    cmavant = distance 
                    vmoy = 0
                    speed = 0
                    tpsinit = time.time()
                    vmax = 0;
                    self.totalisateur_log.info('{}'.format(totalisateur))
                    self.odometre_log.info('{}'.format(distance))
                    distancetmp = 0
                #elif event.key == BOUTON_BACKSPACE:
                    #self.SwitchToScene(TitleScene())

        # Action sur le dérouleur
        if self.case > self.nb_cases - self.ncases :
            self.case = self.nb_cases -self.ncases
        if self.case < 0 :
            self.case = 0

    def Update(self):
        global distance,speed,vmax,cmavant,tps,j,vmoy,distancetmp,temperature,cpu
        global labels,old_labels,sprites,old_sprites,rbconfig
        if self.case != self.oldcase :
            # On sauvegarde la nouvelle position
            rbconfig['Roadbooks']['case'] = str(self.case)
            save_rbconfig()

        if distance < 200000 or tps < 2 : 
            vmoy = 0 # On maintient la vitesse moyenne a 0 sur les 20 premiers metres ou les 2 premieres secondes
        else:
            vmoy = ((distance/(time.time()-tpsinit))*3.6/1000);
            
        k = time.time() - j
        if ( k >= 1) : # Vitesse moyenne sur 1 secondes
            speed = (distance*3.6-cmavant*3.6); 
            speed = 1.0*speed/k/1000; 
            j = time.time()
            cmavant = distance

        if speed > vmax : vmax = speed

        if distancetmp > 100000 : # On sauvegarde l'odometre tous les 100 metres
            self.totalisateur_log.info('{}'.format(totalisateur))
            self.odometre_log.info('{}'.format(distance))
            distancetmp = 0

        labels['heure'] = (time.strftime("%H:%M:%S", time.localtime()), labels['heure'][1],labels['heure'][2],labels['heure'][3])
        labels['distance'] = ('{:6.2f} '.format(distance/1000000), labels['distance'][1],labels['distance'][2],labels['distance'][3])
        labels['vitesse'] = ('{:3.0f}  '.format(speed), labels['vitesse'][1],labels['vitesse'][2],labels['vitesse'][3])
        labels['vmoy'] = ('{:3.0f}  '.format(vmoy), labels['vmoy'][1],labels['vmoy'][2],labels['vmoy'][3])
        labels['temperature'] = ('{:4.1f}C'.format(temperature),labels['temperature'][1],labels['temperature'][2],labels['temperature'][3])
        labels['cpu'] = ('{:4.1f}%'.format(cpu),labels['cpu'][1],labels['cpu'][2],labels['cpu'][3])

        if self.oldcase != self.case :
            if angle == 0 :
                for n in range(self.ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle),(0,480-(n+1)*self.nh))
            else :
                for n in range(self.ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle),(800-(n+1)*self.nh,0))

    def Render(self, screen):
        # Positionnement des différents éléments d'affichage, s'ils ont été modifiés
        update_labels(screen)
        update_sprites(screen)

#*******************************************************************************************************#
#---------------------------------------- Ecran Compteur de vitesse simple -----------------------------#
#*******************************************************************************************************#

class OdometerScene(SceneBase):
    def __init__(self, fname = ''):
        global roue, aimants,developpe, distance,cmavant,distancetmp,distance2,cmavant2,totalisateur,speed,labels, old_labels,sprites, old_sprites,angle,myfont,alphabet,alphabet_size_x,alphabet_size_y
        SceneBase.__init__(self,fname)
        check_configfile()
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        image_cache = {}
        
        speed = 0

        self.orientation = setupconfig['Parametres']['orientation']
        angle = 90 if self.orientation == 'Portrait' else 0

        setup_alphabet (BLANC75)
        setup_alphabet(BLANC25)
        setup_alphabet(BLANC100)
        setup_alphabet(ROUGE25)
        setup_alphabet(BLANC200)

        self.index = 0 # totalisateur par defaut

        # Dans l'ordre : heure,odometre,texte_vitesse,vitesse,texte_vitessemoyenne,vitessemoyenne,
        labels['heure'] = ('00:00:00',(int(guiconfig[self.orientation]['odo_tps_x']),int(guiconfig[self.orientation]['odo_tps_y'])),BLANC75,angle)
        labels['t_totalisateur'] = ('Total : ',(int(guiconfig[self.orientation]['odo_t_km_x']),int(guiconfig[self.orientation]['odo_t_km_y'])),BLANC25,angle)
        labels['totalisateur'] = ('{:6.2f} '.format(0.0),(int(guiconfig[self.orientation]['odo_km_x']),int(guiconfig[self.orientation]['odo_km_y'])),BLANC100,angle)
        labels['t_vitesse'] = ('Vitesse',(int(guiconfig[self.orientation]['odo_t_vi_x']),int(guiconfig[self.orientation]['odo_t_vi_y'])),ROUGE25,angle)
        labels['vitesse'] = ('{:3.0f} '.format(100.0),(int(guiconfig[self.orientation]['odo_vi_x']),int(guiconfig[self.orientation]['odo_vi_y'])),BLANC200,angle)
        labels['temperature'] = ('{:4.1f}C'.format(0.0),(int(guiconfig[self.orientation]['odo_temp_x']),int(guiconfig[self.orientation]['odo_temp_y'])),ROUGE25,angle)
        labels['cpu'] = ('{:4.1f}%'.format(0.0),(int(guiconfig[self.orientation]['odo_cpu_x']),int(guiconfig[self.orientation]['odo_cpu_y'])),ROUGE25,angle)

        roue = int(setupconfig['Parametres']['roue'])
        aimants = int(setupconfig['Parametres']['aimants'])
        developpe = 1.0*roue / aimants

        import logging
        from logging.handlers import RotatingFileHandler

        try :
            with open('/mnt/piusb/.log/odometre.log', "r") as f1:
                last_line = f1.readlines()[-1]
                distance = int(last_line)
        except :
            distance = 0
        cmavant = distance
        distancetmp=0
        self.odometre_log = logging.getLogger('Rotating Odometer Log')
        self.odometre_log.setLevel(logging.INFO)
        self.odometre_handler = RotatingFileHandler('/mnt/piusb/.log/odometre.log',maxBytes=8000,backupCount=20)
        self.odometre_log.addHandler(self.odometre_handler)

        try :
            with open('/mnt/piusb/.log/odometre2.log', "r") as f2:
                last_line = f2.readlines()[-1]
                distance2 = int(last_line)
        except :
            distance2 = 0
        cmavant2 = distance2
        self.odometre2_log = logging.getLogger('Rotating Odometer2 Log')
        self.odometre2_log.setLevel(logging.INFO)
        self.odometre2_handler = RotatingFileHandler('/mnt/piusb/.log/odometre2.log',maxBytes=8000,backupCount=20)
        self.odometre2_log.addHandler(self.odometre2_handler)

        try :
            with open('/mnt/piusb/.log/totalisateur.log', "r") as f2:
                last_line = f2.readlines()[-1]
                totalisateur = int(last_line)
        except :
            totalisateur = 0

        self.totalisateur_log = logging.getLogger('Rotating Totalisateur Log')
        self.totalisateur_log.setLevel(logging.INFO)
        self.totalisateur_handler = RotatingFileHandler('/mnt/piusb/.log/totalisateur.log',maxBytes=8000,backupCount=20)
        self.totalisateur_log.addHandler(self.totalisateur_handler)

        if mode_jour:
            pygame.display.get_surface().fill(BLANC)
        else:
            pygame.display.get_surface().fill(NOIR)
        pygame.display.update()

        j = time.time()

    def ProcessInput(self, events, pressed_keys):
        global distance,cmavant,distance2,cmavant2,speed,tpsinit,distancetmp
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            elif event.type == pygame.KEYDOWN :
                # Seule action possible : reinitialisation du trip partiel
                if event.key == BOUTON_BACKSPACE:
                    if self.index == 1 :
                        distance = 0
                        cmavant = distance
                        speed = 0
                        tpsinit = time.time()
                        # On force la sauvegarde du nouveau trip, notamment si on le fait a l'arret
                        self.totalisateur_log.info('{:3d}'.format(totalisateur))
                        self.odometre_log.info('{:3d}'.format(distance))
                        self.odometre2_log.info('{:3d}'.format(distance2))
                        distancetmp = 0
                    elif self.index == 2 :
                        distance2 = 0
                        cmavant2 = distance2
                        speed = 0
                        tpsinit = time.time()
                        # On force la sauvegarde du nouveau trip, notamment si on le fait a l'arret
                        self.totalisateur_log.info('{}'.format(totalisateur))
                        self.odometre_log.info('{}'.format(distance))
                        self.odometre2_log.info('{}'.format(distance2))
                        distancetmp = 0
                elif event.key == BOUTON_DOWN or event.key == BOUTON_UP :
                    self.index += 1
            elif event.type == GMASSSTORAGE:
                self.SwitchToScene(G_MassStorageScene())

    def Update(self):
        global distance,speed,vmax,cmavant,tps,j,vmoy,distancetmp,distancetmp2,temperature,cpu
        global labels,old_labels,sprites,old_sprites

        if self.index > 2 : self.index = 0

        k = time.time() - j
        if ( k >= 1) : # Vitesse moyenne sur 1 secondes
            speed = (distance*3.6-cmavant*3.6); 
            speed = 1.0*speed/k/1000; 
            j = time.time()
            cmavant = distance

        if distancetmp > 100000 : #On sauvegarde l'odometre tous les 100 metres
            self.totalisateur_log.info('{}'.format(totalisateur))
            self.odometre_log.info('{}'.format(distance))
            self.odometre2_log.info('{}'.format(distance2))
            distancetmp = 0

        if self.next == self :
            labels['heure'] = (time.strftime("%H:%M:%S", time.localtime()), labels['heure'][1],labels['heure'][2],labels['heure'][3])
            d = totalisateur 
            if self.index == 0 :
                d = totalisateur
                t = 'Total :  '
            elif self.index == 1 :
                d = distance 
                t = 'Trip 1 : '
            else :
                d = distance2 
                t = 'Trip 2 : '
            labels['totalisateur'] = ('{:6.2f} '.format(d/1000000), labels['totalisateur'][1],labels['totalisateur'][2],labels['totalisateur'][3])
            labels['t_totalisateur'] = (t, labels['t_totalisateur'][1],labels['t_totalisateur'][2],labels['t_totalisateur'][3])
            labels['vitesse'] = ('{:3.0f}    '.format(speed), labels['vitesse'][1],labels['vitesse'][2],labels['vitesse'][3])
            labels['temperature'] = ('{:4.1f}C'.format(temperature),labels['temperature'][1],labels['temperature'][2],labels['temperature'][3])
            labels['cpu'] = ('{:4.1f}% '.format(cpu),labels['cpu'][1],labels['cpu'][2],labels['cpu'][3])

    def Render(self, screen):
        # Positionnement des différents éléments d'affichage, s'ils ont été modifiés
        update_labels(screen)
        update_sprites(screen)

#*******************************************************************************************************#
#------------------------- La partie Derouleur Zoom   --------------------------------------------------#
#*******************************************************************************************************#
class RoadbookZoomScene(SceneBase):
    def __init__(self, fname = ''):
        global image_cache,filedir,fichiers,rb_ratio,rb_ratio_annot,sprites, old_sprites,angle
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
        rb_ratio_annot = 480/w if self.orientation == 'Portrait' else 600/800
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
        global sprites,old_sprites,rbconfig
        if self.case != self.oldcase :
            # On sauvegarde la nouvelle position
            rbconfig['Roadbooks']['case'] = str(self.case)
            save_rbconfig()
            if angle == 0 :
                for n in range(self.ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle),(0,480-(n+1)*self.nh))
            else :
                for n in range(self.ncases):
                    sprites['{}'.format(n)] = (get_image(self.case+n,angle),(800-(n+1)*self.nh,0))

    def Render(self, screen):
        # Positionnement des différents éléments d'affichage, s'ils ont été modifiés
        update_sprites(screen)


# Pour optimisation
#import cProfile
#cProfile.run ('run_RpiRoadbook(800, 480, 60, TitleScene())')

run_RpiRoadbook(800, 480, TitleScene())
