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

# actions du joueur

def joueur_carte(jeu):
    if jeu["etat"] != "joue":
        return
    m = main_active(jeu)
    m.append(piocher(jeu["paquet"]))
    if bust(m):
        avancer_main(jeu)

def joueur_reste(jeu):
    if jeu["etat"] != "joue":
        return
    avancer_main(jeu)

def joueur_double(jeu):
    if jeu["etat"] != "joue":
        return
    j = joueur_courant(jeu)
    idx = j["main_active"]
    if j["solde"] < j["mises"][idx]:
        return
    j["solde"] -= j["mises"][idx]
    j["mises"][idx] *= 2
    main_active(jeu).append(piocher(jeu["paquet"]))
    avancer_main(jeu)

def joueur_abandonne(jeu):
    if jeu["etat"] != "joue":
        return
    j = joueur_courant(jeu)
    idx = j["main_active"]
    j["solde"] += j["mises"][idx] // 2 # on recupere la moitie
    j["mises"][idx] = 0
    j["fini"] = True
    avancer_si_besoin(jeu)

def joueur_split(jeu):
    if jeu["etat"] != "joue":
        return
    j = joueur_courant(jeu)
    m = main_active(jeu)
    idx = j["main_active"]
    mise = j["mises"][idx]
    if len(m) != 2 or m[0]["valeur"] != m[1]["valeur"] or j["solde"] < mise:
        return
    j["solde"] -= mise
    main1 = [m[0], piocher(jeu["paquet"])]
    main2 = [m[1], piocher(jeu["paquet"])]
    j["mains"].pop(idx)
    j["mises"].pop(idx)
    j["mains"].insert(idx, main2)
    j["mains"].insert(idx, main1)
    j["mises"].insert(idx, mise)
    j["mises"].insert(idx, mise)


# croupier

def retourner_cartes_croupier(jeu):
    # on rend toutes les cartes visibles
    for c in jeu["main_croupier"]:
        c["visible"] = True

def tour_croupier(jeu):
    jeu["etat"] = "tour_croupier"
    retourner_cartes_croupier(jeu)

    # tire a 16 reste a 17
    while score_main(jeu["main_croupier"]) < 17:
        nouvelle = piocher(jeu["paquet"])
        jeu["main_croupier"].append(nouvelle)

    fin_partie(jeu)


# fin de partie

def fin_partie(jeu):
    jeu["etat"] = "fini"
    retourner_cartes_croupier(jeu)
    score_c = score_main(jeu["main_croupier"])
    bj_c = blackjack(jeu["main_croupier"])

    for j in jeu["joueurs"]:
        resultats_j = []
        for k, m in enumerate(j["mains"]):
            mise = j["mises"][k]
            score_j = score_main(m)
            bj_j = blackjack(m)

            if bj_j and bj_c:
                res = "Egalite"; gain = mise
            elif bj_j:
                res = "Blackjack !"; gain = mise + int(mise * 1.5)
            elif bust(m):
                res = "Perdu"; gain = 0
            elif bust(jeu["main_croupier"]):
                res = "Gagne"; gain = mise * 2
            elif score_j > score_c:
                res = "Gagne"; gain = mise * 2
            elif score_j < score_c:
                res = "Perdu"; gain = 0
            else:
                res = "Egalite"; gain = mise

            j["solde"] += gain
            resultats_j.append(res)
        jeu["resultats"][j["nom"]] = resultats_j

    print("resultats: " + str(jeu["resultats"]))


# sauvegarde des scores

FICHIER_SCORES = "scores_blackjack.json"
SOLDE_INITIAL = 1000

def charger_scores():
    if os.path.exists(FICHIER_SCORES):
        with open(FICHIER_SCORES, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder_score(nom, solde_initial, solde_final):
    scores = charger_scores()
    scores.append({"nom": nom, "gain": solde_final - solde_initial, "solde": solde_final})
    with open(FICHIER_SCORES, "w", encoding="utf-8") as f:
        json.dump(scores[-100:], f, ensure_ascii=False, indent=2)


#INTERFACE GRAPHIQUE

# couleurs utilisees
VERT = "#35654d" # fond vert casino
VERT_FONCE = "#1e3d2f" # bordures et header
BLANC = "#ffffff"
NOIR = "#000000"
ROUGE = "#cc0000" # cartes coeur/carreau
JAUNE = "#f0c040" # titre et boutons
GRIS = "#888888" # boutons desactives
ORANGE = "#e65100"
VIOLET = "#6a1b9a"

W_CARTE, H_CARTE = 52, 76

# variables globales
jeu = None
soldes_initiaux = {}
spin_mises = {}

# widgets partages
label_score_croupier = None
frame_cartes_croupier = None
frame_joueurs = None
label_resultat = None
frame_mises = None
btn_carte = btn_rester = btn_double = btn_split = btn_abandonner = None
btn_nouvelle = None


#Design de carte avec canvas
def dessiner_carte(canvas, c):
    # fond blanc de la carte
    canvas.create_rectangle(2, 2, W_CARTE-2, H_CARTE-2, fill=BLANC, outline=NOIR, width=2)

    if c["visible"] == False:
        # dos de carte : rectangle bleu marine avec losanges
        canvas.create_rectangle(2, 2, W_CARTE-2, H_CARTE-2, fill="#1a237e", outline=NOIR, width=2)
        canvas.create_rectangle(7, 7, W_CARTE-7, H_CARTE-7, fill="#283593", outline="#3949ab", width=1)
        canvas.create_text(W_CARTE//2, H_CARTE//2, text="?", font=("Arial", 16, "bold"), fill=BLANC)
    else:
        # on choisit la couleur du texte selon la couleur de la carte
        if c["couleur"] == "coeur" or c["couleur"] == "carreau":
            couleur_texte = ROUGE
        else:
            couleur_texte = NOIR

        # le symbole
        if c["couleur"] == "pique":
            symbole = "♠"
        elif c["couleur"] == "coeur":
            symbole = "♥"
        elif c["couleur"] == "carreau":
            symbole = "♦"
        else:
            symbole = "♣"

        # la valeur en haut a gauche
        canvas.create_text(10, 12, text=c["valeur"], font=("Arial", 8, "bold"), fill=couleur_texte)
        # le symbole au milieu
        canvas.create_text(W_CARTE//2, H_CARTE//2, text=symbole, font=("Arial", 18), fill=couleur_texte)
        # la valeur en bas a droite
        canvas.create_text(W_CARTE-10, H_CARTE-12, text=c["valeur"], font=("Arial", 8, "bold"), fill=couleur_texte)
