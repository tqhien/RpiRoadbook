# RpiRoadbook
Roadbook numérique à partir d'un Raspberry Pi

## Idée de départ

Pour les rallyes moto du Championnat de France de Rallye Routier, ou pour mes propres balades, j'utilise pour l'instant un dérouleur "papier". La version électrique permet avec une télécommande, de faire avance ou reculer les cases du roadbook pour suivre sa navigation. 

Un produit existe pour passer au dérouleur électronique (IzRoadbook, à base de liseuse), mais le prix et le fait que pour l'instant il est destiné uniquement aux rallyes du CFRR ne permettent pas de l'utiliser pour ses propres balades ou de réutiliser la liseuse pour lire ses romans.

Pour mes besoins de création de roadbooks de balade, j'ai donc commencé à coder un site pour générer les cases qui vont bien (accessible [ici](http://tqhien.free.fr/) ). Vient ensuite le moment de développer la partie "terrain" du roadbook : le dérouleur. Les critères sont les suivants : composants accessibles à tout le monde, design différent de ce qui existe, et réutilisation pour autre chose que le dérouleur. Cela se traduit par un écran d'une dimension suffisante (7 pouces), tactile et visible même en plein soleil (800cd/m2). Pas trop cher (le Rasperry Pi est idéal pour ça) et pouvant remplacer le dérouleur et le trip que j'ai actuellement au guidon.

## Approche linux embarquée

Pour un système embarqué sur une moto, la problématique est l'alimentation du rpi et la sécurité de la carte mémoire. Je m'explique. Normalement, avec la distribution Raspbian le rpi fonctionne comme un ordinateur : il lit et écrit sur le disque (la sdcard) en démarrant et doit sauvegarder des choses à l'extinction. En cas de coupure de courant à répétitions, il est fréquent d'aboutir à une corruption de la carte SD et la perte des données.

Le passage à l'embarqué répond à des besoins différents : démarrage rapide et sécurité en cas de coupure de courant. Cela signifie notamment une carte mémoire en lecture seule : pas de corruption de la carte mémoire en cas d'extinction intempestive. Il y a juste une partition de la carte qui est en écriture, pour sauvegarder de temps en temps les données utilisateurs. La création de son propre système d'exploitation est un peu longue à réaliser, car il faut sélectionner les éléments nécessaires et rejeter les autres puis compiler à partir du code source. D'habitude, on crée ces fichiers sur l'architecture qui recevra le système. Par exemple sur PC pour du PC, sur un Mac pour du Mac, etc. Si on le fait sur le Rpi, c'est long. Très long. Donc il s'agit d'utiliser la puissance de son ordinateur pour générer plus rapidement le code que comprendra le Rpi. On appelle cela de la Cross-compilation. C'est l'objet du chapitre suivant : Builroot.

## Buildroot et Raspberry Pi
A venir...


## Application Python / Lecteur de PDF / Trip
A venir...

## Télécommande
A venir...
