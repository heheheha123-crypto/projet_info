import random
import json
import os
import tkinter as tk
from tkinter import messagebox

#cartes

def creer_carte(valeur, couleur, visible=True):
    #on cree un dictionnaire
    return {"valeur": valeur, "couleur": couleur, "visible": visible}

def valeur_carte(c):
    #Valeur de la carte pour le score
    if c["valeur"] in ['J', 'Q', 'K']:
        return 10
    elif c["valeur"] == 'A':
        return 11 #on changera apres
    else:
        return int(c["valeur"]) # on convertit en nombre

def afficher_carte(c):
    #si la carte est visible on l'affiche
    if c["visible"] == True:
        return c["valeur"] + " de " + c["couleur"]
    else:
        return "XX"


# paquet de cartes

def creer_paquet():
    couleurs = ['pique', 'coeur', 'carreau', 'trefle']
    valeurs = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']

    paquet = []
    for coul in couleurs:
        for val in valeurs:
            nouvelle_carte = creer_carte(val, coul)
            paquet.append(nouvelle_carte) # on ajoute au paquet

    random.shuffle(paquet) # on melange
    print("paquet cree")
    return paquet

def piocher(paquet):
    c = paquet.pop() # on prend la derniere carte
    c["visible"] = True
    return c


# la main

def score_main(main):
    total = 0
    for c in main:
        total = total + valeur_carte(c) # on additionne

    # on compte les as
    nb_as = 0
    for c in main:
        if c["valeur"] == 'A':
            nb_as = nb_as + 1

    # si on depasse 21 las vaut 1
    while total > 21 and nb_as > 0:
        total = total - 10 # on enleve 10
        nb_as = nb_as - 1

    return total

def score_visible_croupier(main):
    total = sum(valeur_carte(c) for c in main if c["visible"])
    nb_as = sum(1 for c in main if c["valeur"] == 'A' and c["visible"])
    while total > 21 and nb_as > 0:
        total -= 10
        nb_as -= 1
    return total

def blackjack(main):
    # blackjack: 2 cartes et 21
    if len(main) == 2:
        if score_main(main) == 21:
            return True
    return False

def bust(main):
    # bust: depasse 21
    if score_main(main) > 21:
        return True
    return False

def afficher_main(main):
    cartes = []
    for c in main:
        texte_carte = afficher_carte(c)
        cartes.append(texte_carte) # on ajoute le texte
    resultat = ", ".join(cartes)
    return resultat


# etat du jeu
# chaque joueur a une liste "mains" et une liste "mises" pour gerer le split

def creer_joueur(nom, solde=1000):
    return {"nom": nom, "solde": solde, "mains": [], "mises": [], "main_active": 0, "fini": False}

def creer_partie(joueurs):
    # on cree le dictionnaire du jeu
    jeu = {}
    jeu["paquet"] = []
    jeu["joueurs"] = joueurs
    jeu["joueur_actif"] = 0
    jeu["main_croupier"] = []
    jeu["etat"] = "mises" # mises, joue, tour_croupier, fini
    jeu["resultats"] = {}
    return jeu

def joueur_courant(jeu):
    return jeu["joueurs"][jeu["joueur_actif"]]

def main_active(jeu):
    j = joueur_courant(jeu)
    return j["mains"][j["main_active"]]

def nouvelle_partie(jeu):
    jeu["paquet"] = []
    jeu["main_croupier"] = []
    jeu["etat"] = "mises"
    jeu["joueur_actif"] = 0
    jeu["resultats"] = {}
    for j in jeu["joueurs"]:
        j["mains"] = []
        j["mises"] = []
        j["main_active"] = 0
        j["fini"] = False

def placer_mises(jeu):
    # distribue les cartes apres que les mises ont ete posees
    jeu["paquet"] = creer_paquet()
    for j in jeu["joueurs"]:
        j["mains"] = [[piocher(jeu["paquet"]), piocher(jeu["paquet"])]]

    jeu["main_croupier"] = [piocher(jeu["paquet"])]
    cachee = piocher(jeu["paquet"])
    cachee["visible"] = False
    jeu["main_croupier"].append(cachee)

    print("cartes distribuees")

    jeu["etat"] = "joue"
    jeu["joueur_actif"] = 0

    # blackjack immediat : on passe ce joueur
    for j in jeu["joueurs"]:
        if blackjack(j["mains"][0]):
            j["fini"] = True
    avancer_si_besoin(jeu)


# avancement entre mains et joueurs

def avancer_main(jeu):
    j = joueur_courant(jeu)
    if j["main_active"] + 1 < len(j["mains"]):
        j["main_active"] += 1
        if blackjack(main_active(jeu)):
            avancer_main(jeu)
    else:
        j["fini"] = True
        avancer_si_besoin(jeu)

def avancer_si_besoin(jeu):
    while jeu["joueur_actif"] < len(jeu["joueurs"]):
        if not jeu["joueurs"][jeu["joueur_actif"]]["fini"]:
            return
        jeu["joueur_actif"] += 1
    tour_croupier(jeu)
