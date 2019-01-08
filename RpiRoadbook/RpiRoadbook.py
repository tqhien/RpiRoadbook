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

distance = 0
distancetmp = 0
speed = 0.00
roue = 1864
vmax = 0.00
vmoy = 0.0
tps = 0.0
tpsinit=0.0
cmavant = 0
j = time.time()
temperature = -1
cpu = -1

filedir = ''
fichiers = []

rb_ration = 1

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

#*******************************************************************************************************#
#------------------------- Les callbacks des interruptions GPIO et fonctions utiles --------------------#
#*******************************************************************************************************#
def input_roue_callback(channel):
    global distance,distancetmp
    distance += roue
    distancetmp += roue

def input_left_callback(channel):
    b4_time = time.time()
    bouton_time = time.time() - b4_time
    while GPIO.input(channel) == 0 and bouton_time < 2 : # on attend le retour du bouton ou un appui de plus de 2 secondes 
        bouton_time = time.time() - b4_time
    if bouton_time < 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_LEFT}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_HOME}))

def input_right_callback(channel):
    b4_time = time.time()
    bouton_time = time.time() - b4_time
    while GPIO.input(channel) == 0 and bouton_time < 2 : # on attend le retour du bouton ou un appui de plus de 2 secondes 
        bouton_time = time.time() - b4_time
    if bouton_time < 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_RIGHT}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_END}))

def input_ok_callback(channel):
    b4_time = time.time()
    bouton_time = time.time() - b4_time
    while GPIO.input(channel) == 0 and bouton_time < 2 : # on attend le retour du bouton ou un appui de plus de 2 secondes 
        bouton_time = time.time() - b4_time
    if bouton_time < 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_OK}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_BACKSPACE}))

def input_up_callback(channel):
    b4_time = time.time()
    bouton_time = time.time() - b4_time
    while GPIO.input(channel) == 0 and bouton_time < 2 : # on attend le retour du bouton ou un appui de plus de 2 secondes 
        bouton_time = time.time() - b4_time
    if bouton_time < 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_UP}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGUP}))

def input_down_callback(channel):
    b4_time = time.time()
    bouton_time = time.time() - b4_time
    while GPIO.input(channel) == 0 and bouton_time < 2 : # on attend le retour du bouton ou un appui de plus de 2 secondes 
        bouton_time = time.time() - b4_time
    if bouton_time < 2 :
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_DOWN}))
    else:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_PGDOWN}))

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
        image_cache[(key,angle)] = pygame.transform.rotozoom (pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[key])),angle,rb_ratio)
    return image_cache[(key,angle)]


#-------------------------------------------------------------------------------------------#
#------------------------------ Optimisation des rendus des textes -------------------------#
#-------------------------------------------------------------------------------------------#
alphabet = {}
alphabet_size_x = {}
alphabet_size_y = {}
font25 = ''
font50 = ''
font75 = ''
font100=''
font200=''

labels = {}
old_labels = {}

BLANC = 0
ROUGE = 1
VERT = 2
BLEU = 3
JAUNE = 4
GRIS = 5

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
SALPHA = {'0':25,'1':50,'2':75,'3':100,'4':200,'5':25,'6':50,'7':25,'8':25,'9':25,'10':75}

def setup_alphabet():
    global alphabet,alphabet_size_x,alphabet_size_y,font25,font50,font75,font100,font200
    for i in range(1,256) :
        alphabet[(chr(i),BLANC25,0)] = font25.render(chr(i),0,(255,255,255),(0,0,0))
        alphabet[(chr(i),BLANC25inv,0)] = font25.render(chr(i),0,(0,0,0),(255,255,255))
        alphabet[(chr(i),BLANC50,0)] = font50.render(chr(i),0,(255,255,255),(0,0,0))
        alphabet[(chr(i),BLANC50inv,0)] = font50.render(chr(i),0,(0,0,0),(255,255,255))
        alphabet[(chr(i),BLANC75,0)] = font75.render(chr(i),0,(255,255,255),(0,0,0))
        alphabet[(chr(i),BLANC100,0)] = font100.render(chr(i),0,(255,255,255),(0,0,0))
        alphabet[(chr(i),BLANC200,0)] = font200.render(chr(i),0,(255,255,255),(0,0,0))
        alphabet[(chr(i),ROUGE25,0)] = font25.render(chr(i),0,(255,0,0),(0,0,0))
        alphabet[(chr(i),ROUGE25inv,0)] = font25.render(chr(i),0,(255,0,0),(255,255,255))
        alphabet[(chr(i),VERT25,0)] = font25.render(chr(i),0,(0,255,0),(0,0,0))
        alphabet[(chr(i),GRIS75,0)] = font75.render(chr(i),0,(125,125,125),(0,0,0))
        alphabet[(chr(i),BLANC25,90)] = pygame.transform.rotate (font25.render(chr(i),0,(255,255,255),(0,0,0)),90)
        alphabet[(chr(i),BLANC25inv,90)] = pygame.transform.rotate (font25.render(chr(i),0,(0,0,0),(255,255,255)),90)
        alphabet[(chr(i),BLANC50,90)] = pygame.transform.rotate (font50.render(chr(i),0,(255,255,255),(0,0,0)),90)
        alphabet[(chr(i),BLANC50inv,90)] = pygame.transform.rotate (font50.render(chr(i),0,(0,0,0),(255,255,255)),90)
        alphabet[(chr(i),BLANC75,90)] = pygame.transform.rotate (font75.render(chr(i),0,(255,255,255),(0,0,0)),90)
        alphabet[(chr(i),BLANC100,90)] = pygame.transform.rotate (font100.render(chr(i),0,(255,255,255),(0,0,0)),90)
        alphabet[(chr(i),BLANC200,90)] = pygame.transform.rotate (font200.render(chr(i),0,(255,255,255),(0,0,0)),90)
        alphabet[(chr(i),ROUGE25,90)] = pygame.transform.rotate (font25.render(chr(i),0,(255,0,0),(0,0,0)),90)
        alphabet[(chr(i),ROUGE25inv,90)] = pygame.transform.rotate (font25.render(chr(i),0,(255,0,0),(255,255,255)),90)
        alphabet[(chr(i),VERT25,90)] = pygame.transform.rotate (font25.render(chr(i),0,(0,255,0),(0,0,0)),90)
        alphabet[(chr(i),GRIS75,90)] = pygame.transform.rotate (font75.render(chr(i),0,(125,125,125),(0,0,0)),90)
        alphabet_size_x[(chr(i),25,0)] = alphabet[(chr(i),BLANC25,0)].get_size()[0]
        alphabet_size_y[(chr(i),25,0)] = 0
        alphabet_size_x[(chr(i),25,90)] = 0 
        alphabet_size_y[(chr(i),25,90)] = -alphabet[(chr(i),BLANC25,90)].get_size()[1]
        alphabet_size_x[(chr(i),50,0)] = alphabet[(chr(i),BLANC50,0)].get_size()[0]
        alphabet_size_y[(chr(i),50,0)] = 0
        alphabet_size_x[(chr(i),50,90)] = 0 
        alphabet_size_y[(chr(i),50,90)] = -alphabet[(chr(i),BLANC50,90)].get_size()[1]
        alphabet_size_x[(chr(i),75,0)] = alphabet[(chr(i),BLANC75,0)].get_size()[0]
        alphabet_size_y[(chr(i),75,0)] = 0
        alphabet_size_x[(chr(i),75,90)] = 0 
        alphabet_size_y[(chr(i),75,90)] = -alphabet[(chr(i),BLANC75,90)].get_size()[1]
        alphabet_size_x[(chr(i),100,0)] = alphabet[(chr(i),BLANC100,0)].get_size()[0]
        alphabet_size_y[(chr(i),100,0)] = 0
        alphabet_size_x[(chr(i),100,90)] = 0 
        alphabet_size_y[(chr(i),100,90)] = -alphabet[(chr(i),BLANC100,90)].get_size()[1]
        alphabet_size_x[(chr(i),200,0)] = alphabet[(chr(i),BLANC200,0)].get_size()[0]
        alphabet_size_y[(chr(i),200,0)] = 0
        alphabet_size_x[(chr(i),200,90)] = 0 
        alphabet_size_y[(chr(i),200,90)] = -alphabet[(chr(i),BLANC200,90)].get_size()[1]

def blit_text (screen,st,coords, col=BLANC25,angle=0):
    if (not angle in (0,90)) : angle = 0
    (x,y) = coords
    if angle == 0 :
        for i in range(len(st)) :
            r = screen.blit(alphabet[(st[i],col,angle)],(x,y))
            x += alphabet_size_x[(st[i],SALPHA[str(col)],angle)]
            y += alphabet_size_y[(st[i],SALPHA[str(col)],angle)]
            pygame.display.update(r)
    else :
        for i in range(len(st)) :
            x += alphabet_size_x[(st[i],SALPHA[str(col)],angle)]
            y += alphabet_size_y[(st[i],SALPHA[str(col)],angle)]
            r = screen.blit(alphabet[(st[i],col,angle)],(x,y))
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
#-------------------------- Vérification configfile -------------------------------------------#
#----------------------------------------------------------------------------------------------#

def check_configfile():
    maconfig = configparser.ConfigParser()
    maconfig.read('default.cfg')
    # On essaye de charger celui existant
    try:
        maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
    except:
        # Erreur : pas de fichier de config, on sauvegarde la configuration finale
        with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
            maconfig.write(configfile)

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
def run_RpiRoadbook(width, height, fps, starting_scene):
    global font25,font50,font75,font100,font200
    pygame.display.init() ;
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()

    font25 = pygame.font.SysFont("cantarell", 25)
    font50 = pygame.font.SysFont("cantarell", 50)
    font75 = pygame.font.SysFont("cantarell", 75)
    font100 = pygame.font.SysFont("cantarell", 100)
    font200 = pygame.font.SysFont("cantarell", 200)
    
    setup_alphabet()

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

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        self.SwitchToScene(SelectionScene())

    def Render(self, screen):
        screen.fill((0,0,0))
        pygame.display.update()



#*******************************************************************************************************#
#---------------------------------------- Ecran de sélection du Roadbook -------------------------------#
#*******************************************************************************************************#
class SelectionScene(SceneBase):
    def __init__(self):
        global angle,labels,old_labels,sprites,old_sprites
        SceneBase.__init__(self)

        self.runonce=True

        pygame.font.init()
        check_configfile()
        # On charge le fichier de config
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.orientation = self.maconfig['Parametres']['orientation']

        angle = 90 if self.orientation == 'Portrait' else 0

        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}

        self.menu_config = pygame.image.load('./images/icone_config.jpg')
        self.menu_config_white = pygame.image.load('./images/icone_config_white.jpg')
        sprites['config'] = (self.menu_config,(int(self.maconfig[self.orientation]['select_config_x']),int(self.maconfig[self.orientation]['select_config_y'])))
        self.gotoConfig = False

        if self.orientation == 'Paysage' :
            labels['infos'] = ('Demarrage automatique dans 5s...',(int(self.maconfig[self.orientation]['select_text_x']),int(self.maconfig[self.orientation]['select_text_y'])),VERT25,angle)
            labels['invite'] = ('Selectionnez le roadbook a charger :',(10,10),BLANC25,angle)
            labels['up'] = ('        ',(10,50),BLANC25,angle)
            labels['down'] = ('        ',(10,380),BLANC25,angle)
            for i in range (10) :
                labels['liste{}'.format(i)] = ('',(10,80+i*30),BLANC25,angle)
        else :
            labels['infos'] = ('Demarrage automatique dans 5s...',(int(self.maconfig[self.orientation]['select_text_x']),int(self.maconfig[self.orientation]['select_text_y'])),VERT25,angle)
            labels['invite'] = ('Selectionnez le roadbook a charger :',(0,480),BLANC25,angle)
            labels['up'] = ('        ',(50,480),BLANC25,angle)
            labels['down'] = ('        ',(380,480),BLANC25,angle)
            for i in range (10) :
                labels['liste{}'.format(i)] = ('',(80+i*30,480),BLANC25,angle)

        self.roue = int(self.maconfig['Parametres']['roue'])
        self.countdown = 5 ;
        self.iscountdown = True ;
        self.selection= 0 ;
        self.fenetre = 0 ;
        self.saved = self.maconfig['Roadbooks']['etape'] ;
        self.filenames = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
        if len(self.filenames) == 0 : self.SwitchToScene(NoneScene())
        if self.saved in self.filenames : # le fichier rb existe, on le préselectionne
            self.filename = self.saved 
            self.selection = self.filenames.index(self.filename)
        else : # le fichier rb n'existe plus
            self.filename = ''
        
        self.column = 1
        self.j = time.time()

        pygame.display.get_surface().fill((0,0,0))
        pygame.display.update()



    def ProcessInput(self, events, pressed_keys):
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
                                self.maconfig['Roadbooks']['etape'] = self.filenames[self.selection]
                                self.maconfig['Roadbooks']['case'] = '0'
                                with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                                    self.maconfig.write(configfile)
                            self.k = self.j + self.countdown + 1 # hack pour afficher le message chargement en cours
                            self.SwitchToScene(ConversionScene(self.filename))
                        else :
                            self.gotoConfig = True
            elif event.type == GMASSSTORAGE :
                self.iscountdown = False
                self.SwitchToScene(G_MassStorageScene())

    def Update(self):
        global sprites,old_sprites,labels,old_labels,angle
        if self.gotoConfig :
            self.SwitchToScene(ConfigScene())
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
                        if i == self.selection and self.column==1 :
                            couleur = ROUGE25inv
                        else :
                            couleur = ROUGE25
                    else :
                        text = self.filenames[i]
                        if i == self.selection and self.column==1 :
                            couleur = BLANC25inv
                        else :
                            couleur = BLANC25
                    if self.next == self :
                        labels[p] = (text,labels[p][1],couleur,labels[p][3])
            if self.fenetre+10<len(self.filenames):
                labels['down'] = ('(plus)',labels['down'][1],labels['down'][2],labels['down'][3])

            self.k = time.time()
            if self.next == self:
                sprites['config'] = (self.menu_config_white,sprites['config'][1]) if self.column == 2 else (self.menu_config,sprites['config'][1])
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
                    self.maconfig['Roadbooks']['etape'] = self.filenames[self.selection]
                    with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                        self.maconfig.write(configfile)
                    self.SwitchToScene(ConversionScene(self.filename))


    def Render(self, screen):
        update_labels(screen)
        update_sprites(screen)

#*******************************************************************************************************#
#---------------------------------------- La partie Pas de Roadbooks présents --------------------------#
#*******************************************************************************************************#
class NoneScene(SceneBase):
    def __init__(self, fname = ''):
        global labels,old_labels,sprites,old_sprites
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        labels = {}
        old_labels = {}

        pygame.display.get_surface().fill((0,0,0))
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
#---------------------------------------- La partie Réglages -------------------------------------------#
#*******************************************************************************************************#
class ConfigScene(SceneBase):
    def __init__(self, fname = ''):
        global angle,labels,old_labels,sprites,old_sprites
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        check_configfile()
        pygame.font.init()
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        self.now = time.localtime()
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.orientation = self.maconfig['Parametres']['orientation']

        angle = 90 if self.orientation == 'Portrait' else 0
        if angle == 0 :
            self.bouton_ok = pygame.image.load('./images/ok.jpg')
            self.bouton_ok_white = pygame.image.load('./images/ok_white.jpg')
        else :
            self.bouton_ok = pygame.transform.rotozoom (pygame.image.load('./images/ok.jpg'),90,1)
            self.bouton_ok_white = pygame.transform.rotozoom (pygame.image.load('./images/ok_white.jpg'),90,1)
        

        labels ['t_roue'] = ('Roue :',(int(self.maconfig[self.orientation]['config_l_roue_x']),int(self.maconfig[self.orientation]['config_l_roue_y'])),BLANC50,angle)
        labels ['roue'] = ('{:4d}'.format(0),(int(self.maconfig[self.orientation]['config_roue_x']),int(self.maconfig[self.orientation]['config_roue_y'])),BLANC50,angle)
        labels ['t_orientation'] = ('Orientation :',(int(self.maconfig[self.orientation]['config_l_orientation_x']),int(self.maconfig[self.orientation]['config_l_orientation_y'])),BLANC50,angle)
        labels ['orientation'] = ('Portrait ',(int(self.maconfig[self.orientation]['config_orientation_x']),int(self.maconfig[self.orientation]['config_orientation_y'])),BLANC50,angle)
        labels ['t_dim'] = ('Luminosite :',(int(self.maconfig[self.orientation]['config_l_dim_x']),int(self.maconfig[self.orientation]['config_l_dim_y'])),BLANC50,angle)
        labels ['dim'] = ('100',(int(self.maconfig[self.orientation]['config_dim_x']),int(self.maconfig[self.orientation]['config_dim_y'])),BLANC50,angle)
        labels ['t_date'] = ('Date :',(int(self.maconfig[self.orientation]['config_l_date_x']),int(self.maconfig[self.orientation]['config_l_date_y'])),BLANC50,angle)
        labels ['jj'] = ('01/',(int(self.maconfig[self.orientation]['config_d_x']),int(self.maconfig[self.orientation]['config_d_y'])),BLANC50,angle)
        labels ['mm'] = ('01/',(int(self.maconfig[self.orientation]['config_m_x']),int(self.maconfig[self.orientation]['config_m_y'])),BLANC50,angle,)
        labels ['aaaa'] = ('2018',(int(self.maconfig[self.orientation]['config_y_x']),int(self.maconfig[self.orientation]['config_y_y'])),BLANC50,angle)
        labels ['t_heure'] = ('Heure:',(int(self.maconfig[self.orientation]['config_l_heure_x']),int(self.maconfig[self.orientation]['config_l_heure_y'])),BLANC50,angle)
        labels ['hh'] = ('00:',(int(self.maconfig[self.orientation]['config_hour_x']),int(self.maconfig[self.orientation]['config_hour_y'])),BLANC50,angle)
        labels ['min'] = ('00:',(int(self.maconfig[self.orientation]['config_minute_x']),int(self.maconfig[self.orientation]['config_minute_y'])),BLANC50,angle)
        labels ['ss'] = ('00 ',(int(self.maconfig[self.orientation]['config_seconde_x']),int(self.maconfig[self.orientation]['config_seconde_y'])),BLANC50,angle,)
        sprites ['ok'] = (self.bouton_ok,(int(self.maconfig[self.orientation]['config_ok_x']),int(self.maconfig[self.orientation]['config_ok_y'])))

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.index = 7 # de 0 à 5 : date et heure, 6=ok, 7=roue, 8=orientation, 9 =luminosité
        self.d_roue = int(self.maconfig['Parametres']['roue'])

        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])

        self.paysage = self.maconfig['Parametres']['orientation'] == 'Paysage'
        self.dim = int(self.maconfig['Parametres']['luminosite'])

        pygame.display.get_surface().fill((0,0,0))
        pygame.display.update()
        

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
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
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
                    elif self.index == 7 :
                        self.d_roue -= 1
                        if self.d_roue < 10 : self.d_roue = 10
                    elif self.index == 8 :
                        self.paysage = not self.paysage
                    elif self.index == 9 :
                        self.dim -= 5
                        if self.dim < 5 : self.dim = 5
                        pulse.ChangeDutyCycle(self.dim)
                elif event.key == BOUTON_UP:
                    if self.index < 5 :
                        self.data[self.index] += 1
                        self.update_time()
                    elif self.index == 5:
                        self.data[5] = 0
                        self.update_time()
                    elif self.index == 7:
                        self.d_roue += 1
                        if self.d_roue > 9999 : self.d_roue = 9999
                    elif self.index == 8 :
                        self.paysage = not self.paysage
                    elif self.index == 9 :
                        self.dim += 5
                        if self.dim > 100 : self.dim = 100
                        pulse.ChangeDutyCycle(self.dim)
                elif event.key == BOUTON_OK:
                    # validation
                    if self.index == 7:
                        self.maconfig['Parametres']['roue'] = str(self.d_roue)
                        try:
                            with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                                self.maconfig.write(configfile)
                        except: 
                            pass
                    elif self.index == 8:
                        self.maconfig['Parametres']['orientation'] = 'Paysage' if self.paysage else 'Portrait'
                        subprocess.Popen('sudo ./paysage.sh',shell=True) if self.paysage else subprocess.Popen('sudo ./portrait.sh',shell=True)
                        try:
                            with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                                self.maconfig.write(configfile)
                        except: 
                            pass       
                    elif self.index == 9 :
                        self.maconfig['Parametres']['luminosite'] = str(self.dim)
                        try:
                            with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                                self.maconfig.write(configfile)
                        except: 
                            pass
                    elif self.index == 6 : 
                        self.SwitchToScene(TitleScene())
                    # on passe au réglage suivant
                    self.index +=1
                    if self.index > 9:
                        self.index = 0
            
            
        

    def Update(self):
        global labels,old_labels,sprites,old_sprites
        self.now = time.localtime()
        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])
        labels['jj'] = ('{:02d}/'.format(self.data[0]),labels['jj'][1],BLANC50inv,labels['jj'][3]) if self.index == 0 else ('{:02d}/'.format(self.data[0]),labels['jj'][1],BLANC50,labels['jj'][3])
        labels['mm'] = ('{:02d}/'.format(self.data[1]),labels['mm'][1],BLANC50inv,labels['mm'][3]) if self.index == 1 else ('{:02d}/'.format(self.data[1]),labels['mm'][1],BLANC50,labels['mm'][3])
        labels['aaaa'] = ('{:4d}'.format(self.data[2]),labels['aaaa'][1],BLANC50inv,labels['aaaa'][3]) if self.index == 2 else ('{:4d}'.format(self.data[2]),labels['aaaa'][1],BLANC50,labels['aaaa'][3])
        labels['hh'] = ('{:02d}:'.format(self.data[3]),labels['hh'][1],BLANC50inv,labels['hh'][3]) if self.index == 3 else ('{:02d}:'.format(self.data[3]),labels['hh'][1],BLANC50,labels['hh'][3])
        labels['min'] = ('{:02d}:'.format(self.data[4]),labels['min'][1],BLANC50inv,labels['min'][3]) if self.index == 4 else ('{:02d}:'.format(self.data[4]),labels['min'][1],BLANC50,labels['min'][3])
        labels['ss'] = ('{:02d}'.format(self.data[5]),labels['ss'][1],BLANC50inv,labels['ss'][3]) if self.index == 5 else ('{:02d} '.format(self.data[5]),labels['ss'][1],BLANC50,labels['ss'][3])
        labels['roue'] = ('{:4d}mm'.format(self.d_roue),labels['roue'][1],BLANC50inv,labels['roue'][3]) if self.index == 7 else ('{:4d}mm'.format(self.d_roue),labels['roue'][1],BLANC50,labels['roue'][3])
        labels['dim'] = ('{:3d}%'.format(self.dim),labels['dim'][1],BLANC50inv,labels['dim'][3]) if self.index == 9 else ('{:3d}%'.format(self.dim),labels['dim'][1],BLANC50,labels['dim'][3])
        
        if self.paysage :
            labels['orientation'] = ('Paysage',labels['orientation'][1],BLANC50inv,labels['orientation'][3]) if self.index == 8 else ('Paysage ',labels['orientation'][1],BLANC50,labels['orientation'][3])
        else :
            labels['orientation'] = ('Portrait ',labels['orientation'][1],BLANC50inv,labels['orientation'][3]) if self.index == 8 else ('Portrait ',labels['orientation'][1],BLANC50,labels['orientation'][3])

        sprites['ok'] = (self.bouton_ok_white,sprites['ok'][1]) if self.index == 6 else (self.bouton_ok,sprites['ok'][1])

    def Render(self, screen):
        update_labels(screen)
        update_sprites(screen)
        


#*******************************************************************************************************#
#---------------------------------------- La partie Gadget Mass Storage --------------------------------#
#*******************************************************************************************************#
class G_MassStorageScene(SceneBase):
    def __init__(self, fname = ''):
        global labels,old_labels,sprites,old_sprites
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname

        pygame.font.init()
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
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
                    os.system('modprobe -r g_mass_storage')
                    time.sleep(1)
                    os.system('modprobe g_mass_storage file=/home/rpi/piusb.bin stall=0 ro=0 removable=1')
                    time.sleep(1)
                    os.system('mount -t vfat /home/rpi/piusb.bin /mnt/piusb')
                    time.sleep(1)
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
    def __init__(self, fname = ''):
        global angle, labels,old_labels,sprites,old_sprites
        SceneBase.__init__(self)
        self.next = self
        self.filename = fname
        check_configfile()
        pygame.font.init()

        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.orientation = self.maconfig['Parametres']['orientation']

        angle = 90 if self.orientation == 'Portrait' else 0

        labels = {}
        old_labels = {}
        image_cache = {}

        labels ['text'] = ('',(int(self.maconfig[self.orientation]['conv_text_x']),int(self.maconfig[self.orientation]['conv_text_y'])),VERT25,angle)
        labels ['text1'] = ('',(int(self.maconfig[self.orientation]['conv_text1_x']),int(self.maconfig[self.orientation]['conv_text1_y'])),VERT25,angle)
        labels ['text2'] = ('',(int(self.maconfig[self.orientation]['conv_text2_x']),int(self.maconfig[self.orientation]['conv_text2_y'])),VERT25,angle)
 

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        pass

    def Render(self, screen):
        global labels,old_labels,sprites,old_sprites
        screen.fill((0,0,0))
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
            # On charge le fichier de configuration
            self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
            # On se positionne à l'avant dernière case (ou la 2ème dans l'ordre de lecteur du rb
            self.maconfig['Roadbooks']['case'] = str(total-2)
            with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
              self.maconfig.write(configfile)
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
            # On charge le fichier de configuration
            self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
            if int(self.maconfig['Roadbooks']['case']) < 0 or int(self.maconfig['Roadbooks']['case']) > total -2 :
              # Pb avec la position sauvegardée. On se positionne au début du rb
              self.maconfig['Roadbooks']['case'] = '0'
              with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                self.maconfig.write(configfile)

        self.SwitchToScene(RoadbookScene(self.filename))


#*******************************************************************************************************#
#------------------------- La partie Dérouleur ---------------------------------------------------------#
#*******************************************************************************************************#
class RoadbookScene(SceneBase):
    def __init__(self, fname = ''):
        global distance,image_cache,filedir,fichiers,rb_ratio,labels, old_labels,sprites, old_sprites,angle
        SceneBase.__init__(self,fname)
        check_configfile()
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        filedir = os.path.splitext(self.filename)[0]
        labels = {}
        old_labels = {}
        sprites = {}
        old_sprites = {}
        image_cache = {}

        self.orientation = self.maconfig['Parametres']['orientation']
        angle = 90 if self.orientation == 'Portrait' else 0

        # Dans l'ordre : heure,odometre,texte_vitesse,vitesse,texte_vitessemoyenne,vitessemoyenne,
        labels['heure'] = ('00:00:00',(int(self.maconfig[self.orientation]['rb_tps_x']),int(self.maconfig[self.orientation]['rb_tps_y'])),BLANC75,angle)
        labels['distance'] = ('{:03.2f}'.format(0.0),(int(self.maconfig[self.orientation]['rb_km_x']),int(self.maconfig[self.orientation]['rb_km_y'])),BLANC100,angle)
        labels['t_vitesse'] = ('Vitesse',(int(self.maconfig[self.orientation]['rb_t_vi_x']),int(self.maconfig[self.orientation]['rb_t_vi_y'])),ROUGE25,angle)
        labels['vitesse'] = ('{:3.0f}'.format(0.0),(int(self.maconfig[self.orientation]['rb_vi_x']),int(self.maconfig[self.orientation]['rb_vi_y'])),BLANC75,angle)
        labels['t_vmax'] = ('Vit. max.',(int(self.maconfig[self.orientation]['rb_t_vm_x']),int(self.maconfig[self.orientation]['rb_t_vm_y'])),ROUGE25,angle)
        labels['vmax'] = ('{:3.0f}'.format(0.0),(int(self.maconfig[self.orientation]['rb_vm_x']),int(self.maconfig[self.orientation]['rb_vm_y'])),GRIS75,angle)
        labels['temperature'] = ('{:2.1f}C'.format(0.0),(int(self.maconfig[self.orientation]['rb_temp_x']),int(self.maconfig[self.orientation]['rb_temp_y'])),ROUGE25,angle)
        labels['cpu'] = ('{:2.1f}%'.format(0.0),(int(self.maconfig[self.orientation]['rb_cpu_x']),int(self.maconfig[self.orientation]['rb_cpu_y'])),ROUGE25,angle)
        
        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.ncases = int(self.maconfig[self.orientation]['ncases'])
        self.pages = {}

        import logging
        from logging.handlers import RotatingFileHandler

        try :
            with open('/mnt/piusb/odometre.log', "r") as f1:
                last_line = f1.readlines()[-1]
                distance = int(last_line)
        except :
            distance = 0

        self.odometre_log = logging.getLogger('Rotating Odometer Log')
        self.odometre_log.setLevel(logging.INFO)
        self.odometre_handler = RotatingFileHandler('/mnt/piusb/odometre.log',maxBytes=8000,backupCount=20)
        self.odometre_log.addHandler(self.odometre_handler)

        #Chargement des images
        fichiers = sorted([name for name in os.listdir('/mnt/piusb/Conversions/'+filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+filedir, name))])
        self.nb_cases = len(fichiers)
        self.case = int(self.maconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = 0 # on compte de 0 à longueur-1
        self.oldcase = self.case + 1
        
        samplepage = pygame.image.load (os.path.join('/mnt/piusb/Conversions/'+filedir,fichiers[0]))
        (w,h) = samplepage.get_rect().size
        rb_ratio = min(480/w,150/h) if self.orientation == 'Portrait' else min(600/w,180/h)
        # Mise à l'échelle des images
        self.nh = h * rb_ratio

        pygame.display.get_surface().fill((0,0,0))
        pygame.display.update()

        j = time.time()

    def ProcessInput(self, events, pressed_keys):
        global distance,tpsinit,cmavant,vmoy,vmax
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
                    distance = 0.0
                    cmavant = distance 
                    vmoy = 0
                    speed = 0
                    tpsinit = time.time()/1000
                    vmax = 0;
                elif event.key == BOUTON_OK:
                    self.SwitchToScene(TitleScene())

        # Action sur le dérouleur
        if self.case > self.nb_cases - self.ncases :
            self.case = self.nb_cases -self.ncases
        if self.case < 0 :
            self.case = 0

    def Update(self):
        global distance,speed,vmax,cmavant,tps,j,vmoy,distancetmp,temperature,cpu
        global labels,old_labels,sprites,old_sprites
        if self.case != self.oldcase :
            # On sauvegarde la nouvelle position
            self.maconfig['Roadbooks']['case'] = str(self.case)
            try:
              with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                self.maconfig.write(configfile)
            except: pass

        if distance < 20000 or tps < 2 : 
            vmoy = 0 # On maintient la vitesse moyenne à 0 sur les 20 premiers mètres ou les 2 premières secondes
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
            self.odometre_log.info('{}'.format(distance))
            distancetmp = 0

        labels['heure'] = (time.strftime("%H:%M:%S", time.localtime()), labels['heure'][1],labels['heure'][2],labels['heure'][3])
        labels['distance'] = ('{:3.2f}'.format(distance/1000000), labels['distance'][1],labels['distance'][2],labels['distance'][3])
        labels['vitesse'] = ('{:3.0f}'.format(speed), labels['vitesse'][1],labels['vitesse'][2],labels['vitesse'][3])
        labels['vmax'] = ('{:3.0f}'.format(vmax), labels['vmax'][1],labels['vmax'][2],labels['vmax'][3])
        labels['temperature'] = ('{:2.1f}C'.format(temperature),labels['temperature'][1],labels['temperature'][2],labels['temperature'][3])
        labels['cpu'] = ('{:2.1f}%'.format(cpu),labels['cpu'][1],labels['cpu'][2],labels['cpu'][3])

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



# Pour optimisation
#import cProfile
#cProfile.run ('run_RpiRoadbook(800, 480, 60, TitleScene())')

run_RpiRoadbook(800, 480, 5, TitleScene())
