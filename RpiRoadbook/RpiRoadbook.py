#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 15 08:58:53 2018

@author: Hien TRAN-QUANG
"""

# Pour masquer le message de la version de pygame
import contextlib
with contextlib.redirect_stdout(None):
    import pygame

# Pour l'affichage sur le framebuffer
from pygame.locals import *

(width, height) = (800, 480)
background = (0,0,0) # Fond noir

import time
import os
import re
import configparser

# Pour la lecture des fichiers pdf et conversion en image
from pdf2image import convert_from_path, page_count

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

def run_game(width, height, fps, starting_scene):
    pygame.display.init() ;
    pygame.mouse.set_visible(False)
    screen = pygame.display.set_mode((width, height))
    
    clock = pygame.time.Clock()  

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()
        
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
        
        pygame.display.flip()
        clock.tick(fps)

# The rest is code where you implement your game using the Scenes model 

class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        pygame.font.init()
        self.maconfig = configparser.ConfigParser()

	      # Vérification de l'existence du fichier de config
        try:
	        with open('RpiRoadbook.cfg'): pass
        except IOError:
            with open('RpiRoadbook.cfg', 'w') as configfile:
                self.maconfig['Parametres_Odometre']={}
                self.maconfig['Parametres_Odometre']['roue'] = '1860'
                self.maconfig['Parametres_Odometre']['nb_aimants'] = '1'
                self.maconfig['Parametres_Odometre']['totalisateur'] = '0'
                self.maconfig['Roadbooks'] = {}
                self.maconfig['Roadbooks']['etape'] = ''
                self.maconfig['Roadbooks']['case'] = '-1'
                self.maconfig.write(configfile)

	      # On le charge
        self.maconfig.read('RpiRoadbook.cfg')

        self.j = time.time()
        self.countdown = 6 ;
        self.iscountdown = True ;
        self.selection= 0 ;
        self.saved= self.maconfig['Roadbooks']['etape'] ;
        self.font = pygame.font.SysFont("cantarell", 30)
        self.filenames = [f for f in os.listdir('./../Roadbooks/') if re.search('.pdf$', f)]
        self.filename = self.saved if self.saved in self.filenames  else ''
    
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN :
                self.iscountdown = False ;
                if event.key == pygame.K_RETURN:
                # Move to the next scene when the user pressed Enter 
                    if self.filename != self.filenames[self.selection] :
                        self.filename = self.filenames[self.selection]
                        self.maconfig['Roadbooks']['etape'] = self.filenames[self.selection] 
                        self.maconfig['Roadbooks']['case'] = '-1'
                        with open('RpiRoadbook.cfg', 'w') as configfile:
                            self.maconfig.write(configfile)
                        
                    self.SwitchToScene(RoadbookScene(self.filename))
                elif event.key == pygame.K_UP:
                    self.selection -= 1 ;
                    if self.selection < 0: self.selection = 0 ;
                elif event.key == pygame.K_DOWN:
                    self.selection += 1 ;
                    if self.selection == len(self.filenames): self.selection = len(self.filenames)-1 ;                      
    
    def Update(self):
        if self.iscountdown:
            self.k = time.time();
        #print(k-self.j) ;
            if (self.k-self.j>=self.countdown) :
                self.SwitchToScene(RoadbookScene(self.filename))
    
    def Render(self, screen):
        screen.fill((0, 0, 0))
        invite = self.font.render ('Sélectionnez le roadbook à charger :',0,(255,255,255))
        screen.blit(invite,(10,10))
        for i in range (len(self.filenames)) :
            couleur = (255,0,0) if self.filenames[i] == self.saved else (255,255,255)
            fond = (0,0,255) if i == self.selection else (0,0,0)
            text = self.font.render (self.filenames[i]+' (En cours)', 0, couleur,fond) if self.filenames[i] == self.saved else self.font.render (self.filenames[i], 0, couleur,fond)
            screen.blit (text,(10,40+i*30))
        text = self.font.render('Démarrage automatique dans '+str(int(self.countdown+1-(self.k-self.j)))+'s...', True, (0, 255, 0))
        if self.iscountdown : screen.blit(text,(10,450))
        

class RoadbookScene(SceneBase):
    def __init__(self, fname = ''):
        SceneBase.__init__(self,fname)
        self.maconfig = configparser.ConfigParser()

	      # Vérification de l'existence du fichier de config
        try:
            with open('RpiRoadbook.cfg'): pass
        except IOError:
            with open('RpiRoadbook.cfg', 'w') as configfile:
                self.maconfig['Parametres_Odometre']={}
                self.maconfig['Parametres_Odometre']['roue'] = '1860'
                self.maconfig['Parametres_Odometre']['nb_aimants'] = '1'
                self.maconfig['Parametres_Odometre']['totalisateur'] = '0'
                self.maconfig['Roadbooks'] = {}
                self.maconfig['Roadbooks']['etape'] = ''
                self.maconfig['Roadbooks']['case'] = '-1'
                self.maconfig.write(configfile)
        # On le charge
        self.maconfig.read('RpiRoadbook.cfg')

        #Conversion du fichier de Roadbook en images en mémoire
        self.nb_cases = page_count('./../Roadbooks/'+self.filename)
        self.case = int(self.maconfig['Roadbooks']['case'])
        if self.case < 0 :
            self.case = self.nb_cases - 1 # on compte de 0 à longueur-1, on se place sur l'avant dernière case si 1ère ouverture
        self.oldcase = self.case
        self.pages = convert_from_path('./../Roadbooks/'+self.filename, dpi=150 ,first_page=self.case, last_page=self.case+2, fmt='jpg')

        #on récupère les paramètres de l'image
        self.mode = self.pages[0].mode
        self.size = self.pages [0].size

        # Les 2 seules cases converties
        self.data1 = self.pages [0].tobytes()
        self.data2 = self.pages [1].tobytes()
        self.image1 = pygame.image.fromstring (self.data1,self.size,self.mode)
        self.image2 = pygame.image.fromstring (self.data2,self.size,self.mode)

        pygame.font.init()
        self.font = pygame.font.SysFont("cantarell", 72)
        self.myfont_70 = pygame.font.SysFont("cantarell", 70)
        self.myfont_100 = pygame.font.SysFont("cantarell", 100)

        self.label_tps = self.myfont_70.render("00:00:00", 1, (200,200,200))
        self.label_km = self.myfont_100.render("000.00", 1, (200,200,200))
        self.label_vi = self.myfont_70.render("000", 1, (200,200,200))
        self.label_vm = self.myfont_70.render("000", 1, (100,100,100))
        
    
    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.QUIT:
                self.Terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.Terminate()          
                if event.key == pygame.K_UP:
                    self.oldcase = self.case
                    self.case += 1
                if event.key == pygame.K_DOWN:
                    self.oldcase = self.case
                    self.case -= 1
                if event.key == pygame.K_HOME:
                    self.oldcase = self.case
                    self.case = self.nb_cases -1
                if event.key == pygame.K_END:
                    self.oldcase = self.case
                    self.case = 0

        # Action sur le dérouleur
        if self.case > self.nb_cases - 1 :
            self.case = self.nb_cases -1
        if self.case < 0 :
            self.case = 0

        # On sauvegarde la position en cours
        self.maconfig['Roadbooks']['case'] = str(self.case)
        with open('RpiRoadbook.cfg', 'w') as configfile:
            self.maconfig.write(configfile)
        
    def Update(self):
        if self.case != self.oldcase :
            self.pages = convert_from_path('./../Roadbooks/'+self.filename, dpi=150 ,first_page=self.case, last_page=self.case+2, fmt='jpg')

            self.data1 = self.pages [0].tobytes()
            self.data2 = self.pages [1].tobytes()
    
            self.image1 = pygame.image.fromstring (self.data1,self.size,self.mode)
            self.image2 = pygame.image.fromstring (self.data2,self.size,self.mode)
    
    def Render(self, screen):
        screen.fill(background)
	    # Positionnement des différents éléments d'affichage
        screen.blit(self.label_tps, (10, 5))
        screen.blit(self.label_km, (440, -10))
        screen.blit(self.label_vi, (650, 150))
        screen.blit(self.label_vm, (650, 350))
        screen.blit (self.image1,(0,100))
        screen.blit (self.image2,(0,300))
        
        

run_game(800, 480, 60, TitleScene())
