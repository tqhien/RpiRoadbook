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
import serial
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
temperature = -100
cpu = -1

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

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_ROUE, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Capteur de vitesse
GPIO.setup(GPIO_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
        pass

def cpu_load():
    global cpu
    try:
        with open ('/proc/loadavg','r') as f:
            cpu = int(float(f.readline().split(" ")[:3][0])*100)
    except:
        cpu = -1

#On définit les interruptions sur les GPIO des commandes
GPIO.add_event_detect(GPIO_ROUE, GPIO.FALLING, callback=input_roue_callback,bouncetime=15)
GPIO.add_event_detect(GPIO_LEFT, GPIO.FALLING, callback=input_left_callback, bouncetime=200)
GPIO.add_event_detect(GPIO_RIGHT, GPIO.FALLING, callback=input_right_callback, bouncetime=200)
GPIO.add_event_detect(GPIO_OK, GPIO.FALLING, callback=input_ok_callback, bouncetime=200)
GPIO.add_event_detect(GPIO_UP, GPIO.FALLING, callback=input_up_callback, bouncetime=200)
GPIO.add_event_detect(GPIO_DOWN, GPIO.FALLING, callback=input_down_callback, bouncetime=200)

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
    pygame.display.init() ;
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((width, height))

    clock = pygame.time.Clock()

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

        pygame.display.flip()
        clock.tick(fps)
    GPIO.cleanup()




#*******************************************************************************************************#
#---------------------------------------- Ecran de sélection du Roadbook -------------------------------#
#*******************************************************************************************************#
class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        pygame.font.init()
        check_configfile()
        # On charge le fichier de config
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.orientation = self.maconfig['Parametres']['orientation']
        self.select_config_x = int(self.maconfig[self.orientation]['select_config_x'])
        self.select_config_y = int(self.maconfig[self.orientation]['select_config_y'])
        self.select_text_x = int(self.maconfig[self.orientation]['select_text_x'])
        self.select_text_y = int(self.maconfig[self.orientation]['select_text_y'])
        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.roue = int(self.maconfig['Parametres']['roue'])
        self.countdown = 4 ;
        self.iscountdown = True ;
        self.selection= 0 ;
        self.fenetre = 0 ;
        self.saved = self.maconfig['Roadbooks']['etape'] ;
        self.font = pygame.font.SysFont("cantarell", 24)
        self.filenames = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
        if len(self.filenames) == 0 : self.SwitchToScene(NoneScene())
        if self.saved in self.filenames : # le fichier rb existe, on le préselectionne
            self.filename = self.saved 
            self.selection = self.filenames.index(self.filename)
        else : # le fichier rb n'existe plus
            self.filename = ''
        self.menu_config = pygame.image.load('./images/icone_config.jpg')
        self.menu_config_white = pygame.image.load('./images/icone_config_white.jpg')
        self.column = 1
        self.j = time.time()


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
                            self.SwitchToScene(ConfigScene()) 
            elif event.type == GMASSSTORAGE :
                self.iscountdown = False
                self.SwitchToScene(G_MassStorageScene())

    def Update(self):
        if self.iscountdown:
            self.k = time.time();
            if (self.k-self.j>=self.countdown) :
                self.maconfig['Roadbooks']['etape'] = self.filenames[self.selection]
                with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                    self.maconfig.write(configfile)
                self.SwitchToScene(ConversionScene(self.filename))

    def Render(self, screen):
        img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
        img_tmp.fill((0,0,0))
        invite = self.font.render ('Sélectionnez le roadbook à charger :',0,(255,255,255))
        img_tmp.blit(invite,(10,10))
        if self.fenetre > 0 :
            fleche_up = self.font.render('(moins)',0,(100,100,100))
            img_tmp.blit (fleche_up,(10,50))
        for i in range (len(self.filenames)) :
            if i >= self.fenetre and i <self.fenetre+10 :
                couleur = (255,0,0) if self.filenames[i] == self.saved else (255,255,255)
                fond = (0,0,255) if i == self.selection and self.column==1 else (0,0,0)
                text = self.font.render (self.filenames[i]+' (En cours)', 0, couleur,fond) if self.filenames[i] == self.saved else self.font.render (self.filenames[i], 0, couleur,fond)
                img_tmp.blit (text,(10,80+(i-self.fenetre)*30))
        if self.fenetre+10<len(self.filenames):
            fleche_up = self.font.render('(plus)',0,(100,100,100))
            img_tmp.blit (fleche_up,(10,380))
        img_tmp.blit(self.menu_config_white,(self.select_config_x,self.select_config_y)) if self.column == 2 else img_tmp.blit(self.menu_config,(self.select_config_x,self.select_config_y))    
        if self.iscountdown :
            if self.k-self.j>= self.countdown :
                text = self.font.render('Chargement du roadbook... Veuillez patienter.',True,(0,255,0))
            else :
                text = self.font.render('Démarrage automatique dans '+str(int(self.countdown+1-(self.k-self.j)))+'s...', True, (0, 255, 0))
            img_tmp.blit(text,(self.select_text_x,self.select_text_y))
        if self.orientation == 'Portrait' :
            img_tmp=pygame.transform.rotate (img_tmp,90)
        screen.blit(img_tmp,(0,0))
        pygame.display.flip()

#*******************************************************************************************************#
#---------------------------------------- La partie Pas de Roadbooks présents --------------------------#
#*******************************************************************************************************#
class NoneScene(SceneBase):
    def __init__(self, fname = ''):
        self.next = self
        self.filename = fname
        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 24)
        #self.img = pygame.image.load('./../Roadbooks/images/nothing.jpg')
        self.text1 = self.font.render('Aucun roadbook present.', True, (200, 0, 0))
        self.text2 = self.font.render('Appuyez sur un bouton pour revenir', True, (200, 0, 0))
        self.text3 = self.font.render('au menu apres telechargement', True, (200, 0, 0))

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
        screen.fill((0,0,0))
        screen.blit(self.text1, (100, 200))
        screen.blit(self.text2, (100, 230))
        screen.blit(self.text3, (100, 260))
        pygame.display.flip()

#*******************************************************************************************************#
#---------------------------------------- La partie Réglages -------------------------------------------#
#*******************************************************************************************************#
class ConfigScene(SceneBase):
    def __init__(self, fname = ''):
        self.next = self
        self.filename = fname
        check_configfile()
        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 70)
        self.now = time.localtime()
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.orientation = self.maconfig['Parametres']['orientation']
        self.config_l_roue_x = int(self.maconfig[self.orientation]['config_l_roue_x'])
        self.config_l_roue_y = int(self.maconfig[self.orientation]['config_l_roue_y'])
        self.config_roue_x = int(self.maconfig[self.orientation]['config_roue_x'])
        self.config_roue_y = int(self.maconfig[self.orientation]['config_roue_y'])
        self.config_l_orientation_x = int(self.maconfig[self.orientation]['config_l_orientation_x'])
        self.config_l_orientation_y = int(self.maconfig[self.orientation]['config_l_orientation_y'])
        self.config_orientation_x = int(self.maconfig[self.orientation]['config_orientation_x'])
        self.config_orientation_y = int(self.maconfig[self.orientation]['config_orientation_y'])
        self.config_l_date_x = int(self.maconfig[self.orientation]['config_l_date_x'])
        self.config_l_date_y = int(self.maconfig[self.orientation]['config_l_date_y'])
        self.config_d_x = int(self.maconfig[self.orientation]['config_d_x'])
        self.config_d_y = int(self.maconfig[self.orientation]['config_d_y'])
        self.config_m_x = int(self.maconfig[self.orientation]['config_m_x'])
        self.config_m_y = int(self.maconfig[self.orientation]['config_m_y'])
        self.config_y_x = int(self.maconfig[self.orientation]['config_y_x'])
        self.config_y_y = int(self.maconfig[self.orientation]['config_y_y'])
        self.config_l_heure_x = int(self.maconfig[self.orientation]['config_l_heure_x'])
        self.config_l_heure_y = int(self.maconfig[self.orientation]['config_l_heure_y'])
        self.config_hour_x = int(self.maconfig[self.orientation]['config_hour_x'])
        self.config_hour_y = int(self.maconfig[self.orientation]['config_hour_y'])
        self.config_minute_x = int(self.maconfig[self.orientation]['config_minute_x'])
        self.config_minute_y = int(self.maconfig[self.orientation]['config_minute_y'])
        self.config_seconde_x = int(self.maconfig[self.orientation]['config_seconde_x'])
        self.config_seconde_y = int(self.maconfig[self.orientation]['config_seconde_y'])
        self.config_ok_x = int(self.maconfig[self.orientation]['config_ok_x'])
        self.config_ok_y = int(self.maconfig[self.orientation]['config_ok_y'])

        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.index = 7 # de 0 à 5 : date et heure, 6=ok, 7=roue, 8=orientation
        self.label_roue = self.font.render('Roue : ',True,(200,200,200))
        self.d_roue = int(self.maconfig['Parametres']['roue'])

        self.label_date = self.font.render('Date : ',True,(200,200,200))
        self.label_heure = self.font.render ('Heure:',True,(200,200,200))
        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])

        self.label_orientation = self.font.render('Orientation : ',True,(200,200,200))
        self.paysage = self.maconfig['Parametres']['orientation'] == 'Paysage'
        
        self.bouton_ok = pygame.image.load('./images/ok.jpg')
        self.bouton_ok_white = pygame.image.load('./images/ok_white.jpg')

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
                    if self.index > 8:
                        self.index = 0
                elif event.key == BOUTON_LEFT:
                    self.index -= 1
                    if self.index < 0 :
                        self.index = 8    
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
                        try:
                            with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                                self.maconfig.write(configfile)
                        except: 
                            pass       
                    elif self.index == 6 : 
                        self.SwitchToScene(TitleScene())
                    # on passe au réglage suivant
                    self.index +=1
                    if self.index > 8:
                        self.index = 0
            
            
        

    def Update(self):
        self.now = time.localtime()
        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])
        self.d = self.font.render('{:02d}/'.format(self.data[0]),True,(200,200,200),(0,0,200)) if self.index == 0 else self.font.render('{:02d}/'.format(self.data[0]),True,(200,200,200))
        self.m = self.font.render('{:02d}/'.format(self.data[1]),True,(200,200,200),(0,0,200)) if self.index == 1 else self.font.render('{:02d}/'.format(self.data[1]),True,(200,200,200))
        self.y = self.font.render('{}'.format(self.data[2]),True,(200,200,200),(0,0,200)) if self.index == 2 else self.font.render('{}'.format(self.data[2]),True,(200,200,200))
        self.hour = self.font.render('{:02d}:'.format(self.data[3]),True,(200,200,200),(0,0,200)) if self.index == 3 else self.font.render('{:02d}:'.format(self.data[3]),True,(200,200,200))
        self.minute = self.font.render('{:02d}:'.format(self.data[4]),True,(200,200,200),(0,0,200)) if self.index == 4 else self.font.render('{:02d}:'.format(self.data[4]),True,(200,200,200))
        self.second = self.font.render('{:02d}'.format(self.data[5]),True,(200,200,200),(0,0,200)) if self.index == 5 else self.font.render('{:02d}'.format(self.data[5]),True,(200,200,200))
        self.t_roue = self.font.render('{} mm'.format(self.d_roue),True,(200,200,200),(0,0,200)) if self.index == 7 else self.font.render('{} mm'.format(self.d_roue),True,(200,200,200))
        if self.paysage :
            self.t_orientation = self.font.render('Paysage',True,(200,200,200),(0,0,200)) if self.index == 8 else self.font.render('Paysage',True,(200,200,200))
        else :
            self.t_orientation = self.font.render('Portrait',True,(200,200,200),(0,0,200)) if self.index == 8 else self.font.render('Portrait',True,(200,200,200))

    def Render(self, screen):
        img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
        img_tmp.fill((0,0,0))
        img_tmp.blit(self.label_roue, (self.config_l_roue_x, self.config_l_roue_y))
        img_tmp.blit(self.t_roue, (self.config_roue_x, self.config_roue_y))
        img_tmp.blit(self.label_orientation, (self.config_l_orientation_x, self.config_l_orientation_y))
        img_tmp.blit(self.t_orientation, (self.config_orientation_x, self.config_orientation_y))
        img_tmp.blit(self.label_date, (self.config_l_date_x, self.config_l_date_y))
        img_tmp.blit(self.d, (self.config_d_x, self.config_d_y))
        img_tmp.blit(self.m, (self.config_m_x, self.config_m_y))
        img_tmp.blit(self.y, (self.config_y_x, self.config_y_y))
        img_tmp.blit(self.label_heure,(self.config_l_heure_x, self.config_l_heure_y))
        img_tmp.blit(self.hour, (self.config_hour_x, self.config_hour_y))
        img_tmp.blit(self.minute, (self.config_minute_x, self.config_minute_y))
        img_tmp.blit(self.second, (self.config_seconde_x, self.config_seconde_y))
        
        img_tmp.blit(self.bouton_ok_white,(self.config_ok_x, self.config_ok_y)) if self.index == 6 else img_tmp.blit(self.bouton_ok,(self.config_ok_x, self.config_ok_y))

        if self.orientation == 'Portrait' :
            img_tmp=pygame.transform.rotate (img_tmp,90)
        screen.blit(img_tmp,(0,0))
        


#*******************************************************************************************************#
#---------------------------------------- La partie Gadget Mass Storage --------------------------------#
#*******************************************************************************************************#
class G_MassStorageScene(SceneBase):
    def __init__(self, fname = ''):
        self.next = self
        self.filename = fname
        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 24)
        self.usb_connected = pygame.image.load ('./images/usb_connected_white.jpg')
        self.text = self.font.render('Appuyez sur un bouton une fois le cable debranche pour retourner au menu',True,(200,0,0))
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
        screen.fill((0, 0, 0))
        screen.blit(self.usb_connected, (0, 0))
        screen.blit(self.text,(10,450))
        pygame.display.flip()



#*******************************************************************************************************#
#------------------------- La partie Conversion en Image d'un fichier ----------------------------------#
#*******************************************************************************************************#
class ConversionScene(SceneBase):
    def __init__(self, fname = ''):
        self.next = self
        self.filename = fname
        check_configfile()
        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 24)
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.orientation = self.maconfig['Parametres']['orientation']
        self.conv_text_x = int(self.maconfig[self.orientation]['conv_text_x'])
        self.conv_text_y = int(self.maconfig[self.orientation]['conv_text_y'])
        self.conv_text1_x = int(self.maconfig[self.orientation]['conv_text1_x'])
        self.conv_text1_y = int(self.maconfig[self.orientation]['conv_text1_y'])
        self.conv_text2_x = int(self.maconfig[self.orientation]['conv_text2_x'])
        self.conv_text2_y= int(self.maconfig[self.orientation]['conv_text2_y'])
        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        pass

    def Render(self, screen):
        text1 = self.font.render('Preparation du roadbook... Patience...', True, (0, 255, 0))
        filedir = os.path.splitext(self.filename)[0]
        if os.path.isdir('/mnt/piusb/Conversions/'+filedir) == False: # Pas de répertoire d'images, on convertit le fichier
            os.mkdir('/mnt/piusb/Conversions/'+filedir)

			# on vérifie le format de la page :
            width, height = page_size ('/mnt/piusb/'+self.filename)
            if width > height :
                text2 = self.font.render('Conversion des cases en cours...', True, (0, 255, 0))
                total = page_count ('/mnt/piusb/'+self.filename)
                for i in range (total) :
                    screen.fill((0,0,0))
                    img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
                    img_tmp.fill((0,0,0))
                    img_tmp.blit(text1,(self.conv_text1_x,self.conv_text1_y))
                    img_tmp.blit(text2,(self.conv_text2_x,self.conv_text2_y))
                    text = self.font.render('Case {}/{}'.format(i,total), True, (0, 255, 0))
                    img_tmp.blit(text,(self.conv_text_x,self.conv_text_y))
                    self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = total-i, last_page=total-i, dpi=150, singlefile='{:03}'.format(i+1), fmt='jpg')
                    if self.orientation == 'Portrait' :
                        img_tmp=pygame.transform.rotate (img_tmp,90)
                    screen.blit(img_tmp,(0,0))
                    pygame.display.flip()
            else:
                # conversion et découpage des cases
                text2 = self.font.render('Format Tripy. Conversion en cours...', True, (0, 255, 0))

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
                        text = self.font.render('Case {}/{}'.format(i*nb_cases+j+1,total), True, (0, 255, 0))
                        screen.fill((0,0,0))
                        img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
                        img_tmp.fill((0,0,0))
                        img_tmp.blit(text1,(self.conv_text1_x,self.conv_text1_y))
                        img_tmp.blit(text2,(self.conv_text2_x,self.conv_text2_y))
                        img_tmp.blit(text,(self.conv_text_x,self.conv_text_y))
                        self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile='{:03}'.format(i*nb_cases+j),fmt='jpg')
                        if self.orientation == 'Portrait' :
                            img_tmp=pygame.transform.rotate (img_tmp,90)
                        screen.blit(img_tmp,(0,0))
                        pygame.display.flip()
            # On charge le fichier de configuration
            self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
            # On se positionne à l'avant dernière case (ou la 2ème dans l'ordre de lecteur du rb
            self.maconfig['Roadbooks']['case'] = str(total-2)
            with open('RpiRoadbook.cfg', 'w') as configfile:
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
                    text2 = self.font.render('Pas le meme nombre de cases ! On verifie...', True, (0, 255, 0))
                    for i in range (total) :
                        screen.fill((0,0,0))
                        img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
                        img_tmp.fill((0,0,0))
                        img_tmp.blit(text1,(self.conv_text1_x,self.conv_text1_y))
                        img_tmp.blit(text2,(self.conv_text2_x,self.conv_text2_y))
                        text = self.font.render('Case {}/{}'.format(i,total), True, (0, 255, 0))
                        img_tmp.blit(text,(self.conv_text_x,self.conv_text_y))
                        self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = total-i, last_page=total-i, dpi=150, singlefile='{:03}'.format(i+1), fmt='jpg')
                        if self.orientation == 'Portrait' :
                            img_tmp=pygame.transform.rotate (img_tmp,90)
                        screen.blit(img_tmp,(0,0))
                        pygame.display.flip()
            else :
                # Format Tripy
                #print('Verification coherence Format Tripy')
                nb_ligne = 8
                #Nombre de case par page
                nb_cases = nb_ligne * 2
                total = nb_pages * nb_cases
                nb_images = len([f for f in os.listdir('/mnt/piusb/Conversions/'+filedir) if re.search('.jpg$', f)])
                if total != nb_images :
                    text2 = self.font.render('Pas le meme nombre de cases ! On verifie...', True, (0, 255, 0))
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
                            screen.fill((0,0,0))
                            img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
                            img_tmp.fill((0,0,0))
                            img_tmp.blit(text1,(self.conv_text1_x,self.conv_text1_y))
                            img_tmp.blit(text2,(self.conv_text2_x,self.conv_text2_y))
                            img_tmp.blit(text,(self.conv_text_x,self.conv_text_y))
                            self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile='{:03}'.format(i*nb_cases+j),fmt='jpg')
                            if self.orientation == 'Portrait' :
                                img_tmp=pygame.transform.rotate (img_tmp,90)
                            screen.blit(img_tmp,(0,0))
                            pygame.display.flip()
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
        global distance
        SceneBase.__init__(self,fname)
        check_configfile()
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.filedir = os.path.splitext(self.filename)[0]
        self.orientation = self.maconfig['Parametres']['orientation']
        self.rb_tps_x = int(self.maconfig[self.orientation]['rb_tps_x'])
        self.rb_tps_y = int(self.maconfig[self.orientation]['rb_tps_y'])
        self.rb_km_x = int(self.maconfig[self.orientation]['rb_km_x'])
        self.rb_km_y = int(self.maconfig[self.orientation]['rb_km_y'])
        self.rb_t_vi_x = int(self.maconfig[self.orientation]['rb_t_vi_x'])
        self.rb_t_vi_y = int(self.maconfig[self.orientation]['rb_t_vi_y'])
        self.rb_vi_x = int(self.maconfig[self.orientation]['rb_vi_x'])
        self.rb_vi_y = int(self.maconfig[self.orientation]['rb_vi_y'])
        self.rb_t_vm_x = int(self.maconfig[self.orientation]['rb_t_vm_x'])
        self.rb_t_vm_y = int(self.maconfig[self.orientation]['rb_t_vm_y'])
        self.rb_vm_x = int(self.maconfig[self.orientation]['rb_vm_x'])
        self.rb_vm_y = int(self.maconfig[self.orientation]['rb_vm_y'])
        self.rb_temp_x = int(self.maconfig[self.orientation]['rb_temp_x'])
        self.rb_temp_y = int(self.maconfig[self.orientation]['rb_temp_y'])
        self.rb_cpu_x = int(self.maconfig[self.orientation]['rb_cpu_x'])
        self.rb_cpu_y = int(self.maconfig[self.orientation]['rb_cpu_y'])
        (self.imgtmp_w,self.imgtmp_h) = (480,800) if self.orientation == 'Portrait' else (800,480)
        self.ncases = int(self.maconfig[self.orientation]['ncases'])

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
        fichiers = sorted([name for name in os.listdir('/mnt/piusb/Conversions/'+self.filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+self.filedir, name))])
        self.nb_cases = len(fichiers)
        self.case = int(self.maconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = 0 # on compte de 0 à longueur-1
        self.oldcase = self.case
        self.pages = []
        for i in fichiers:
            self.pages.append (pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+self.filedir,i)))  # On a converti toutes les images. c'est plus long au début mais plus réactif ensuite et on peut rajouter des annotations
        (w,h) = self.pages[0].get_rect().size
        ratio = min(480/w,200/h) if self.orientation == 'Portrait' else min(600/w,200/h)
        # Mise à l'échelle des images
        self.nh = h * ratio
        for i in range(len(self.pages)):
            self.pages [i] = pygame.transform.rotozoom (self.pages[i],0,ratio)

        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 72)
        self.myfont_36 = pygame.font.SysFont("cantarell", 36)
        self.myfont_70 = pygame.font.SysFont("cantarell", 70)
        self.myfont_100 = pygame.font.SysFont("cantarell", 100)

        self.label_tps = self.myfont_70.render("00:00:00", 1, (200,200,200))
        self.label_km = self.myfont_100.render("000.00", 1, (200,200,200))
        self.label_vi = self.myfont_70.render("000", 1, (200,200,200))
        self.label_vm = self.myfont_70.render("000", 1, (100,100,100))

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
                elif event.key == BOUTON_OK:
                    distance = 0.0
                    cmavant = distance 
                    vmoy = 0
                    speed = 0
                    tpsinit = time.time()/1000
                    vmax = 0;
                elif event.key == BOUTON_BACKSPACE:
                    self.SwitchToScene(TitleScene())

        # Action sur le dérouleur
        if self.case > self.nb_cases - self.ncases :
            self.case = self.nb_cases -self.ncases
        if self.case < 0 :
            self.case = 0

    def Update(self):
        global distance,speed,vmax,cmavant,tps,j,vmoy,distancetmp,temperature,cpu
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

        self.label_tps = self.myfont_70.render(time.strftime("%H:%M:%S", time.localtime()), 1, (200,200,200))
        self.label_km = self.myfont_100.render('{0:.2f}'.format(distance/1000000), 1, (200,200,200))
        self.label_t_vi = self.myfont_36.render('Vitesse',1,(200,0,0))
        self.label_vi = self.myfont_70.render('{0:.1f}'.format(speed), 1, (200,200,200))
        self.label_t_vm = self.myfont_36.render('VMax',1,(200,0,0))
        self.label_vm = self.myfont_70.render('{0:.1f}'.format(vmax), 1, (100,100,100))

        self.label_temp = self.myfont_36.render('{0:.1f}°C'.format(temperature),1,(200,200,200))
        self.label_cpu = self.myfont_36.render('{}%'.format(cpu),1,(200,200,200))

    def Render(self, screen):
        img_tmp = pygame.Surface ((self.imgtmp_w,self.imgtmp_h)) 
        img_tmp.fill((0,0,0))
        # Positionnement des différents éléments d'affichage
        img_tmp.blit(self.label_tps, (self.rb_tps_x, self.rb_tps_y))
        img_tmp.blit(self.label_km, (self.rb_km_x, self.rb_km_y))
        img_tmp.blit(self.label_t_vi,(self.rb_t_vi_x, self.rb_t_vi_y))
        img_tmp.blit(self.label_vi, (self.rb_vi_x, self.rb_vi_y))
        img_tmp.blit(self.label_t_vm, (self.rb_t_vm_x, self.rb_t_vm_y))
        img_tmp.blit(self.label_vm, (self.rb_vm_x, self.rb_vm_y))
        for n in range(self.ncases):
            img_tmp.blit (self.pages[self.case+n],(0,self.imgtmp_h-(n+1)*self.nh))
        img_tmp.blit(self.label_temp,(self.rb_temp_x, self.rb_temp_y))
        img_tmp.blit(self.label_cpu,(self.rb_cpu_x,self.rb_cpu_y))
        if self.orientation == 'Portrait' :
            img_tmp=pygame.transform.rotate (img_tmp,90)
        screen.blit(img_tmp,(0,0))



# Pour optimisation
#import cProfile
#cProfile.run ('run_RpiRoadbook(800, 480, 60, TitleScene())')

run_RpiRoadbook(800, 480, 5, TitleScene())
