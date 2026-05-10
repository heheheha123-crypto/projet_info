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



def activer_boutons():
    btn_carte.config(state="normal", bg="#4caf50")
    btn_rester.config(state="normal", bg="#2196f3")
    btn_double.config(state="normal", bg=ORANGE)
    btn_split.config(state="normal", bg=VIOLET)
    btn_abandonner.config(state="normal", bg="#f44336")

    j = joueur_courant(jeu)
    m = main_active(jeu)
    mise = j["mises"][j["main_active"]]

    # double seulement si solde suffisant
    peut_double = j["solde"] >= mise
    btn_double.config(state="normal" if peut_double else "disabled", bg=ORANGE if peut_double else GRIS)

    # split seulement si 2 cartes identiques et solde suffisant
    peut_split = (len(m) == 2 and m[0]["valeur"] == m[1]["valeur"] and j["solde"] >= mise)
    btn_split.config(state="normal" if peut_split else "disabled", bg=VIOLET if peut_split else GRIS)

def desactiver_boutons():
    for btn in [btn_carte, btn_rester, btn_double, btn_split, btn_abandonner]:
        btn.config(state="disabled", bg=GRIS)


def rafraichir():
    # on efface les anciennes cartes du croupier
    for widget in frame_cartes_croupier.winfo_children():
        widget.destroy()

    # on efface la zone joueurs
    for widget in frame_joueurs.winfo_children():
        widget.destroy()

    # on redessine les cartes du croupier
    for c in jeu["main_croupier"]:
        canvas = tk.Canvas(frame_cartes_croupier, width=W_CARTE, height=H_CARTE, bg=VERT, highlightthickness=0)
        canvas.pack(side="left", padx=3)
        dessiner_carte(canvas, c)

    label_score_croupier.config(text="croupier  -  score : " + str(score_visible_croupier(jeu["main_croupier"])))

    idx_actif = jeu["joueur_actif"]
    for ji, j in enumerate(jeu["joueurs"]):
        est_actif = (jeu["etat"] == "joue" and ji == idx_actif)
        fond = "#2a6e3f" if est_actif else VERT_FONCE
        bordure = JAUNE if est_actif else VERT_FONCE

        frame_j = tk.Frame(frame_joueurs, bg=fond, highlightbackground=bordure, highlightthickness=2, padx=5, pady=3)
        frame_j.pack(fill="x", padx=4, pady=2)

        tk.Label(frame_j, text=j["nom"] + "  -  solde : " + str(j["solde"]) + " €",
                 font=("Arial", 10, "bold"), bg=fond, fg=JAUNE if est_actif else BLANC).pack(anchor="w")

        for mi, m in enumerate(j["mains"]):
            est_main_active = est_actif and mi == j["main_active"]
            mise = j["mises"][mi] if mi < len(j["mises"]) else 0
            tag = " <<" if est_main_active else ""

            frame_main = tk.Frame(frame_j, bg=fond)
            frame_main.pack(anchor="w")

            tk.Label(frame_main,
                     text="  Main " + str(mi+1) + "  mise : " + str(mise) + " €  score : " + str(score_main(m)) + tag,
                     font=("Arial", 9), bg=fond, fg=JAUNE if est_main_active else "#aaaaaa").pack(anchor="w")

            frame_cartes = tk.Frame(frame_main, bg=fond)
            frame_cartes.pack(anchor="w")
            for c in m:
                cv = tk.Canvas(frame_cartes, width=W_CARTE, height=H_CARTE, bg=fond, highlightthickness=0)
                cv.pack(side="left", padx=2, pady=2)
                dessiner_carte(cv, c)

        # resultats si la partie est finie
        if jeu["etat"] == "fini" and j["nom"] in jeu["resultats"]:
            for res in jeu["resultats"][j["nom"]]:
                coul = {"Gagne": "#69f0ae", "Blackjack !": JAUNE, "Perdu": "#ff5252", "Egalite": BLANC}.get(res, BLANC)
                tk.Label(frame_j, text=res, font=("Arial", 11, "bold"), bg=fond, fg=coul).pack(anchor="w")

    # on active ou desactive les boutons selon letat du jeu
    if jeu["etat"] == "joue":
        activer_boutons()
        label_resultat.config(text="")
    elif jeu["etat"] == "fini":
        desactiver_boutons()
        label_resultat.config(text="")
        for j in jeu["joueurs"]:
            sauvegarder_score(j["nom"], soldes_initiaux.get(j["nom"], SOLDE_INITIAL), j["solde"])


# phase de mises

def afficher_phase_mises():
    global spin_mises
    for w in frame_mises.winfo_children():
        w.destroy()
    spin_mises = {}

    tk.Label(frame_mises, text="Placez vos mises :", font=("Arial", 11, "bold"), bg=VERT_FONCE, fg=JAUNE).grid(row=0, column=0, columnspan=2, pady=(4, 6))

    for i, j in enumerate(jeu["joueurs"]):
        tk.Label(frame_mises, text=j["nom"] + "  (solde : " + str(j["solde"]) + " €)", font=("Arial", 10), bg=VERT_FONCE, fg=BLANC).grid(row=i+1, column=0, sticky="e", padx=8, pady=2)
        spin = tk.Spinbox(frame_mises, from_=10, to=min(j["solde"], 500), increment=10, width=6, font=("Arial", 10), justify="center")
        spin.delete(0, "end")
        spin.insert(0, "50")
        spin.grid(row=i+1, column=1, padx=8, pady=2)
        spin_mises[j["nom"]] = spin

    tk.Button(frame_mises, text="Distribuer", font=("Arial", 10, "bold"), bg=JAUNE, fg=NOIR, relief="flat", command=valider_mises).grid(row=len(jeu["joueurs"])+1, column=0, columnspan=2, pady=8, padx=16, sticky="ew")

    desactiver_boutons()
    label_resultat.config(text="")

def valider_mises():
    for j in jeu["joueurs"]:
        try:
            mise = int(spin_mises[j["nom"]].get())
        except ValueError:
            mise = 50
        mise = max(10, min(mise, j["solde"]))
        j["mises"].append(mise)
        j["solde"] -= mise

    for w in frame_mises.winfo_children():
        w.destroy()

    placer_mises(jeu)
    rafraichir()


#fonctions des boutons

def clic_carte():
    joueur_carte(jeu)
    rafraichir()

def clic_rester():
    joueur_reste(jeu)
    rafraichir()

def clic_double():
    joueur_double(jeu)
    rafraichir()

def clic_abandonner():
    joueur_abandonne(jeu)
    rafraichir()

def clic_split():
    joueur_split(jeu)
    rafraichir()

def clic_nouvelle_partie():
    nouvelle_partie(jeu)
    for widget in frame_cartes_croupier.winfo_children():
        widget.destroy()
    for widget in frame_joueurs.winfo_children():
        widget.destroy()
    label_score_croupier.config(text="croupier  -  score : 0")
    label_resultat.config(text="")
    desactiver_boutons()
    afficher_phase_mises()

