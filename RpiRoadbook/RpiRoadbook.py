#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 08:58:53 2018

@author: Hien TRAN-QUANG
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
j = 0
cmavant = 0
bouton_time = time.time()
temperature = -100

CAPTEUR_ROUE    = USEREVENT # Odometre
BOUTON_LEFT     = pygame.K_LEFT # Bouton left (tout en haut)
BOUTON_RIGHT    = pygame.K_RIGHT # Bouton right (2eme en haut)
BOUTON_OK       = pygame.K_RETURN # Bouton OK/select (au milieu)
BOUTON_UP       = pygame.K_UP # Bouton Up (1er en bas)
BOUTON_DOWN     = pygame.K_DOWN # Bouton Down (tout en bas)
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
#------------------------- Les callbacks des interruptions GPIO  ---------------------------------------#
#*******************************************************************************************************#
def input_roue_callback(channel):
    global distance,distancetmp
    distance += roue
    distancetmp += roue

def input_left_callback(channel):
    global bouton_time
    b4_time = time.time()
    while GPIO.input(channel) == 0 : # on attend le retour du bouton
        pass
    bouton_time = time.time() - b4_time
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_LEFT}))

def input_right_callback(channel):
    global bouton_time
    b4_time = time.time()
    while GPIO.input(channel) == 0 : # on attend le retour du bouton
        pass
    bouton_time = time.time() - b4_time
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_RIGHT}))

def input_ok_callback(channel):
    global bouton_time
    b4_time = time.time()
    while GPIO.input(channel) == 0 : # on attend le retour du bouton
        pass
    bouton_time = time.time() - b4_time
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_OK}))

def input_up_callback(channel):
    global bouton_time
    b4_time = time.time()
    while GPIO.input(channel) == 0 : # on attend le retour du bouton
        pass
    bouton_time = time.time() - b4_time
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_UP}))

def input_down_callback(channel):
    global bouton_time
    b4_time = time.time()
    while GPIO.input(channel) == 0 : # on attend le retour du bouton
        pass
    bouton_time = time.time() - b4_time
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key':BOUTON_DOWN}))

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

#On définit les interruptions sur les GPIO des commandes
GPIO.add_event_detect(GPIO_ROUE, GPIO.FALLING, callback=input_roue_callback)
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
    # On commence par charger le fichier par défaut
    maconfig.read('default.cfg')
    # On essaye de charger celui existant, en écrasant les paramètres par défaut s'ils sont définis
    try:
        maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
    except:
        pass
    # On sauvegarde la configuration finale
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
        # On ne checke la connectivité usb que toutes les 5 secondes
        if time.time() - 5 > t_usb : 
            g_mass_storage_callback()
            t_usb = time.time()   
            rpi_temp()    

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

        self.roue = int(self.maconfig['Parametres_Odometre']['roue'])
        self.countdown = 4 ;
        self.iscountdown = True ;
        self.selection= 0 ;
        self.fenetre = 0 ;
        self.saved= self.maconfig['Roadbooks']['etape'] ;
        self.font = pygame.font.SysFont("cantarell", 24)
        self.filenames = [f for f in os.listdir('/mnt/piusb/') if re.search('.pdf$', f)]
        if len(self.filenames) == 0 : self.SwitchToScene(NoneScene())
        self.filename = self.saved if self.saved in self.filenames  else ''
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
                    if self.column < 1 : self.column = 1
                elif event.key == BOUTON_RIGHT :
                    self.iscountdown = False
                    self.column += 1
                    if self.column > 2 : self.column = 2        
                elif event.key == BOUTON_OK :
                        self.iscountdown = False ;
                        if self.column == 1 :
                            if self.filename != self.filenames[self.selection] :
                                self.filename = self.filenames[self.selection]
                                self.maconfig['Roadbooks']['etape'] = self.filenames[self.selection]
                                self.maconfig['Roadbooks']['case'] = '-1'
                                with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                                    self.maconfig.write(configfile)
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
        screen.fill((0, 0, 0))
        invite = self.font.render ('Sélectionnez le roadbook à charger :',0,(255,255,255))
        screen.blit(invite,(10,10))
        if self.fenetre > 0 :
            fleche_up = self.font.render('(moins)',0,(100,100,100))
            screen.blit (fleche_up,(10,50))
        for i in range (len(self.filenames)) :
            if i >= self.fenetre and i <self.fenetre+10 :
                couleur = (255,0,0) if self.filenames[i] == self.saved else (255,255,255)
                fond = (0,0,255) if i == self.selection else (0,0,0)
                text = self.font.render (self.filenames[i]+' (En cours)', 0, couleur,fond) if self.filenames[i] == self.saved else self.font.render (self.filenames[i], 0, couleur,fond)
                screen.blit (text,(10,80+(i-self.fenetre)*30))
        if self.fenetre+10<len(self.filenames):
            fleche_up = self.font.render('(plus)',0,(100,100,100))
            screen.blit (fleche_up,(10,380))
        screen.blit(self.menu_config_white,(750,430)) if self.column == 2 else screen.blit(self.menu_config,(750,430))    
        if self.iscountdown :
            if self.k-self.j>= self.countdown :
                text = self.font.render('Chargement du roadbook... Veuillez patienter.',True,(0,255,0))
            else :
                text = self.font.render('Démarrage automatique dans '+str(int(self.countdown+1-(self.k-self.j)))+'s...', True, (0, 255, 0))
            screen.blit(text,(10,450))
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
            elif event.type = pygame.KEYDOWN :
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
        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 70)
        self.now = time.localtime()
        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.index = 0
        self.label_date = self.font.render('Date : ',True,(200,200,200))
        self.label_heure = self.font.render ('Heure:',True,(200,200,200))
        self.label_roue = self.font.render('Roue : ',True,(200,200,200))
        self.data = []
        self.data.extend([self.now.tm_mday,self.now.tm_mon,self.now.tm_year,self.now.tm_hour,self.now.tm_min,self.now.tm_sec])
        self.data.extend([int(self.maconfig['Parametres_Odometre']['roue'])])
        self.bouton_ok = pygame.image.load('./images/ok.jpg')
        self.bouton_ok_white = pygame.image.load('./images/ok_white.jpg')

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == pygame.K_HOME:
                    self.oldcase = self.case
                    self.case = self.nb_cases -1
                elif event.key == pygame.K_END:
                    self.oldcase = self.case
                    self.case = 1
                elif event.key == BOUTON_RIGHT:
                    self.index+=1
                    if self.index > 7:
                        self.index = 0
                elif event.key == BOUTON_LEFT:
                    self.index -= 1
                    if self.index < 0 :
                        self.index = 7    
                elif event.key == BOUTON_DOWN:
                    self.data[self.index] -= 1
                elif event.key == BOUTON_UP:
                    self.data[self.index] += 1
                elif event.key == BOUTON_OK:
                    # validation
                    subprocess.call ('sudo rw')
                    subprocess.call ('sudo date "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"'.format(self.data[2],self.data[1],self.data[0],self.data[3],self.data[4],self.data[5]))
                    subprocess.call ('sudo hwclock --set --date "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}"'.format(self.data[2],self.data[1],self.data[0],self.data[3],self.data[4],self.data[5]))
                    subprocess.call ('sudo ro')
                    self.maconfig['Parametres_Odometre']['roue'] = str(self.data[6])
                    try:
                        with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                            self.maconfig.write(configfile)
                    except: pass
                    if self.index == 7 : self.SwitchToScene(TitleScene())
            # Vérification validité des valeurs
            if self.data[2] < 2018 : self.data[2] = 2018
            if self.data[1] < 1 : self.data[1] = 1
            if self.data[1] > 12 : self.data[1] = 12
            if self.data[0] < 1 : self.data[0] = 1
            if self.data[0] > 31 : self.data[0] = 31
            # Vérification de la validité de la date
            try:
                datetime.datetime(self.data[2],self.data[1],self.data[1])
            except ValueError :
                self.data[0] -= 1
            # Validité de l'heure
            if self.data[3] < 0 : self.data[3] = 0
            if self.data[3] > 23 : self.data[3] = 23
            if self.data[4] < 0 : self.data[4] = 0
            if self.data[4] > 59 : self.data[4] = 59 
            if self.data[5] < 0 : self.data[5] = 0
            if self.data[5] < 59 : self.data[5] = 59
            # Validité du développement de la roue
            if self.data[6] < 10 : self.data[6] = 10
            if self.data[6] > 9999 : self.data[6] = 9999
        

    def Update(self):
        self.d = self.font.render('{:02d}/'.format(self.data[0]),True,(200,200,200),(0,0,200)) if self.index == 0 else self.font.render('{:02d}/'.format(self.data[0]),True,(200,200,200))
        self.m = self.font.render('{:02d}/'.format(self.data[1]),True,(200,200,200),(0,0,200)) if self.index == 1 else self.font.render('{:02d}/'.format(self.data[1]),True,(200,200,200))
        self.y = self.font.render('{}'.format(self.data[2]),True,(200,200,200),(0,0,200)) if self.index == 2 else self.font.render('{}'.format(self.data[2]),True,(200,200,200))
        self.hour = self.font.render('{:02d}:'.format(self.data[3]),True,(200,200,200),(0,0,200)) if self.index == 3 else self.font.render('{:02d}:'.format(self.data[3]),True,(200,200,200))
        self.minute = self.font.render('{:02d}:'.format(self.data[4]),True,(200,200,200),(0,0,200)) if self.index == 4 else self.font.render('{:02d}:'.format(self.data[4]),True,(200,200,200))
        self.second = self.font.render('{:02d}'.format(self.data[5]),True,(200,200,200),(0,0,200)) if self.index == 5 else self.font.render('{:02d}'.format(self.data[5]),True,(200,200,200))
        self.d_roue = self.font.render('{} mm'.format(self.data[6]),True,(200,200,200),(0,0,200)) if self.index == 6 else self.font.render('{} mm'.format(self.data[6]),True,(200,200,200))

    def Render(self, screen):
        screen.fill((0,0,0))
        screen.blit(self.label_date, (10, 50))
        screen.blit(self.d, (200, 50))
        screen.blit(self.m, (300, 50))
        screen.blit(self.y, (400, 50))
        screen.blit(self.label_heure,(10,200))
        screen.blit(self.hour, (250, 200))
        screen.blit(self.minute, (350, 200))
        screen.blit(self.second, (450, 200))
        screen.blit(self.label_roue, (10, 350))
        screen.blit(self.d_roue, (200, 350))
        screen.blit(self.bouton_ok_white,(750,430)) if self.index == 7 else screen.blit(self.bouton_ok,(750,430))
        pygame.display.flip()
        


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
        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 24)

    def ProcessInput(self, events, pressed_keys):
        pass

    def Update(self):
        pass

    def Render(self, screen):
        text1 = self.font.render('Preparation du roadbook... Patience...', True, (0, 255, 0))
        self.maconfig = configparser.ConfigParser()
        filedir = os.path.splitext(self.filename)[0]
        if os.path.isdir('/mnt/piusb/Conversions/'+filedir) == False: # Pas de répertoire d'images, on convertit le fichier
            os.mkdir('/mnt/piusb/Conversions/'+filedir)

			# on vérifie le format de la page :
            width, height = page_size ('/mnt/piusb/'+self.filename)
            if width > height :
                text2 = self.font.render('Conversion des cases en cours...', True, (0, 255, 0))
                total = page_count ('/mnt/piusb/'+self.filename)
                for i in range (total) :
                    screen.fill((0, 0, 0))
                    screen.blit(text1,(100,200))
                    screen.blit(text2,(100,230))
                    text = self.font.render('Case {}/{}'.format(i,total), True, (0, 255, 0))
                    screen.blit(text,(100,260))
                    self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , fmt='jpg')
                    pygame.display.flip()
            else:
                # conversion et découpage des cases
                screen.fill((0, 0, 0))
                screen.blit(text1,(100,200))
                text2 = self.font.render('Format Tripy. Conversion en cours...', True, (0, 255, 0))
                screen.blit(text2,(100,230))
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

                for i in reversed(range (nb_pages)) :
                    for j in reversed(range (nb_cases)):
                        if j < nb_ligne :
                            x = round(0)
                            y = round(marge_up+(nb_ligne-j-1)*hauteur)
                        else :
                            x = round(milieu)
                            y = round(marge_up+(2*nb_ligne-j-1)*hauteur)
                        text = self.font.render('Case {}/{}'.format(i*nb_cases+j+1,total), True, (0, 255, 0))
                        screen.fill((0, 0, 0))
                        screen.blit(text1,(100,200))
                        screen.blit(text2,(100,230))
                        screen.blit(text,(100,260))
                        self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile=str(total-i*nb_cases-j),fmt='jpg')
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
                        screen.fill((0, 0, 0))
                        screen.blit(text1,(100,200))
                        screen.blit(text2,(100,230))
                        text = self.font.render('Case {}/{}'.format(i,total), True, (0, 255, 0))
                        screen.blit(text,(100,260))
                        self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , fmt='jpg')
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

                    for i in reversed(range (nb_pages)) :
                        for j in reversed(range (nb_cases)):
                            if j < nb_ligne :
                                x = round(0)
                                y = round(marge_up+(nb_ligne-j-1)*hauteur)
                            else :
                                x = round(milieu)
                                y = round(marge_up+(2*nb_ligne-j-1)*hauteur)
                            screen.fill((0, 0, 0))
                            screen.blit(text1,(100,200))
                            screen.blit(text2,(100,230))
                            text = self.font.render('Case {}/{}'.format(i*nb_cases+j+1,total), True, (0, 255, 0))
                            screen.blit(text,(100,260))
                            self.pages = convert_from_path('/mnt/piusb/'+self.filename, output_folder='/mnt/piusb/Conversions/'+filedir,first_page = i+1, last_page=i+1, dpi=150 , x=x,y=y,w=w,h=h,singlefile=str(total-i*nb_cases-j),fmt='jpg')
                            pygame.display.flip()
            # On charge le fichier de configuration
            self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
            if int(self.maconfig['Roadbooks']['case']) < 0 or int(self.maconfig['Roadbooks']['case']) > total -2 :
              # Pb avec la position sauvegardée. On se positionne à l'avant dernière case (ou la 2ème dans l'ordre de lecteur du rb
              self.maconfig['Roadbooks']['case'] = str(total-2)
              with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                self.maconfig.write(configfile)

        self.SwitchToScene(RoadbookScene(self.filename))


#*******************************************************************************************************#
#------------------------- La partie Dérouleur ---------------------------------------------------------#
#*******************************************************************************************************#
class RoadbookScene(SceneBase):
    def __init__(self, fname = ''):
        SceneBase.__init__(self,fname)

        self.maconfig = configparser.ConfigParser()
        self.maconfig.read('/mnt/piusb/RpiRoadbook.cfg')
        self.filedir = os.path.splitext(self.filename)[0]

        #Chargement des images
        fichiers = [name for name in os.listdir('/mnt/piusb/Conversions/'+self.filedir) if os.path.isfile(os.path.join('/mnt/piusb/Conversions/'+self.filedir, name))]
        self.nb_cases = len(fichiers)
        self.case = int(self.maconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = self.nb_cases - 2 # on compte de 0 à longueur-1, on se place sur l'avant dernière case si 1ère ouverture
        self.oldcase = self.case
        self.pages = []
        for i in fichiers:
            self.pages.append (pygame.image.load(os.path.join('/mnt/piusb/Conversions/'+self.filedir,i)))  # On a converti toutes les images. c'est plus long au début mais plus réactif ensuite et on peut rajouter des annotations

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
        global distance,tpsinit,cmavant,j,vmoy,vmax,bouton_time
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()
                elif event.key == BOUTON_RIGHT:
                    distance+=10000
                    cmavant=distance
                    j = time.time()
                elif event.key == BOUTON_LEFT:
                    distance-=10000
                    if distance <= 0 : distance = 0
                    cmavant = distance
                    j = time.time();
                elif event.key == BOUTON_DOWN:
                    self.oldcase = self.case
                    self.case -= 1
                    if bouton_time >= 2.0 :
                        self.case = 0
                elif event.key == BOUTON_UP:
                    self.oldcase = self.case
                    self.case += 1
                    if bouton_time >= 2.0 :
                        self.case = self.nb_cases - 2
                elif event.key == BOUTON_OK:
                    if bouton_time >= 2.0 :
                        self.SwitchToScene(TitleScene())
                    else:
                        distance = 0.0
                        cmavant = distance 
                        vmoy = 0
                        speed = 0
                        tpsinit = time.time()/1000
                        vmax = 0;

        # Action sur le dérouleur
        if self.case > self.nb_cases - 2 :
            self.case = self.nb_cases -2
        if self.case < 0 :
            self.case = 0

    def Update(self):
        global distance,speed,vmax,cmavant,tps,j,vmoy,distancetmp,temperature
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
            self.maconfig['Parametres_Odometre']['totalisateur'] = str(distance)
            try:
              with open('/mnt/piusb/RpiRoadbook.cfg', 'w') as configfile:
                self.maconfig.write(configfile)
            except: pass
            distancetmp = 0

        self.label_tps = self.myfont_70.render(time.strftime("%H:%M:%S", time.localtime()), 1, (200,200,200))
        self.label_km = self.myfont_100.render('{0:.2f}'.format(distance/1000000), 1, (200,200,200))
        self.label_t_vi = self.myfont_36.render('Vitesse',1,(200,0,0))
        self.label_vi = self.myfont_70.render('{0:.1f}'.format(speed), 1, (200,200,200))
        self.label_t_vm = self.myfont_36.render('VMax',1,(200,0,0))
        self.label_vm = self.myfont_70.render('{0:.1f}'.format(vmax), 1, (100,100,100))

        self.label_temp = self.myfont_36.render('{0:.1f}°C'.format(temperature),1,(200,200,200))

    def Render(self, screen):
        screen.fill((0,0,0))
	    # Positionnement des différents éléments d'affichage
        screen.blit(self.label_tps, (10, 5))
        screen.blit(self.label_km, (600, -10))
        screen.blit(self.label_t_vi,(630,120))
        screen.blit(self.label_vi, (700, 200))
        screen.blit(self.label_t_vm, (630,320))
        screen.blit(self.label_vm, (700, 400))
        screen.blit (self.pages[self.case],(0,100))
        screen.blit (self.pages[self.case+1],(0,300))
        screen.blit(self.label_temp,(300,5))



# Pour optimisation
#import cProfile
#cProfile.run ('run_RpiRoadbook(800, 480, 60, TitleScene())')

run_RpiRoadbook(800, 480, 60, TitleScene())
