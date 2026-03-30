import random

#cartes

def creer_carte(valeur, couleur, visible=True):
    #on cree un dictionnaire
    return {
        "valeur": valeur,
        "couleur": couleur,
        "visible": visible
    }

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

def blackjack(main):
    # blackjack: 2 cartes et 21
    if len(main) == 2:
        if score_main(main) == 21:
            return True
    return False

def bust(main):
    # bust:  depasse 21
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

def creer_partie():
    # on cree le dictionnaire du jeu
    jeu = {}
    jeu["paquet"] = []
    jeu["main_joueur"] = []
    jeu["main_croupier"] = []
    jeu["etat"] = "joue" # joue, tour_croupier, fini
    jeu["resultat"] = None # gagne perdu egalité blackjack abandon
    return jeu

def nouvelle_partie(jeu):
    jeu["paquet"] = creer_paquet()
    jeu["main_joueur"] = [] # on cree une main vide
    jeu["main_croupier"] = []
    jeu["etat"] = "joue"
    jeu["resultat"] = None

    #distribution: 2 cartes visiblespour le joueur, 1 visible et 1 cachee pour le croupier
    jeu["main_joueur"].append(piocher(jeu["paquet"]))
    jeu["main_croupier"].append(piocher(jeu["paquet"]))
    jeu["main_joueur"].append(piocher(jeu["paquet"]))

    carte_cachee = piocher(jeu["paquet"])
    carte_cachee["visible"] = False # on cache la carte
    jeu["main_croupier"].append(carte_cachee)

    print("cartes distribuees")

    #verification blackjack
    if blackjack(jeu["main_joueur"]):
        fin_partie(jeu)


# actions du joueur

def joueur_carte(jeu):
    if jeu["etat"] != "joue":
        return

    nouvelle = piocher(jeu["paquet"])
    jeu["main_joueur"].append(nouvelle)

    if bust(jeu["main_joueur"]):
        fin_partie(jeu)

def joueur_reste(jeu):
    if jeu["etat"] != "joue":
        return
    tour_croupier(jeu)

def joueur_double(jeu):
    if jeu["etat"] != "joue":
        return

    nouvelle = piocher(jeu["paquet"])
    jeu["main_joueur"].append(nouvelle)

    if bust(jeu["main_joueur"]):
        fin_partie(jeu)
    else:
        tour_croupier(jeu)

def joueur_abandonne(jeu):
    if jeu["etat"] != "joue":
        return
    jeu["resultat"] = "Abandon"
    jeu["etat"] = "fini"
    retourner_cartes_croupier(jeu)

def split(jeu):
    if jeu["etat"] != "joue":
        return
    if len(jeu["main_joueur"]) != 2:
        return
    if jeu["main_joueur"][0]["valeur"] != jeu["main_joueur"][1]["valeur"]:
        return

    # on split la main en deux
    main1 = [jeu["main_joueur"][0]]
    main2 = [jeu["main_joueur"][1]]

    # on ajoute une carte a chaque main
    main1.append(piocher(jeu["paquet"]))
    main2.append(piocher(jeu["paquet"]))


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
    score_j = score_main(jeu["main_joueur"])
    score_c = score_main(jeu["main_croupier"])


    if blackjack(jeu["main_joueur"]):
        if blackjack(jeu["main_croupier"]):
            jeu["resultat"] = "Egalite"
        else:
            jeu["resultat"] = "Blackjack !"
    elif bust(jeu["main_joueur"]):
        jeu["resultat"] = "Perdu"
    elif bust(jeu["main_croupier"]):
        jeu["resultat"] = "Gagne"
    elif score_j > score_c:
        jeu["resultat"] = "Gagne"
    elif score_j < score_c:
        jeu["resultat"] = "Perdu"
    else:
        jeu["resultat"] = "Egalite"

    print("resultat: " + jeu["resultat"])


# score des cartes visibles du croupier

def score_visible_croupier(jeu):
    # on compte que les cartes visibles
    if jeu["etat"] == "joue":
        total = 0
        for c in jeu["main_croupier"]:
            if c["visible"] == True:
                total = total + valeur_carte(c) # on additionne
        return total
    else:
        return score_main(jeu["main_croupier"])







#INTERFACE GRAPHIQUE

import tkinter as tk


# couleurs utilisees 
VERT = "#35654d" # fond vert casino
VERT_FONCE = "#1e3d2f" # bordures et header
BLANC = "#ffffff"
NOIR = "#000000"
ROUGE = "#cc0000" # cartes coeur/carreau
JAUNE = "#f0c040" # titre et bouton nouvelle partie
GRIS = "#cccccc" # boutons desactives


#fenetre principale
fenetre = tk.Tk()
fenetre.title("Blackjack")
fenetre.configure(bg=VERT_FONCE)
fenetre.resizable(False, False)


#etat du jeu global
jeu = creer_partie()

#Design de carte avec canvas
def dessiner_carte(canvas, c):
    # fond blanc de la carte
    canvas.create_rectangle(5, 5, 75, 115, fill=BLANC, outline=NOIR, width=2)

    if c["visible"] == False:
        # dos de carte : rectangle bleu marine avec losanges
        canvas.create_rectangle(5, 5, 75, 115, fill="#1a237e", outline=NOIR, width=2)
        canvas.create_rectangle(12, 12, 68, 108, fill="#283593", outline="#3949ab", width=1)
        canvas.create_text(40, 60, text="?", font=("Arial", 28, "bold"), fill=BLANC)
    else:
        # on choisit la couleur du texte selon la couleur de la carte
        if c["couleur"] == "coeur" or c["couleur"] == "carreau":
            couleur_texte = ROUGE
        else:
            couleur_texte = NOIR

        # la valeur en haut a gauche
        canvas.create_text(18, 20, text=c["valeur"], font=("Arial", 13, "bold"), fill=couleur_texte)

        # le symbole au milieu
        if c["couleur"] == "pique":
            symbole = "♠"
        elif c["couleur"] == "coeur":
            symbole = "♥"
        elif c["couleur"] == "carreau":
            symbole = "♦"
        else:
            symbole = "♣"

        canvas.create_text(40, 60, text=symbole, font=("Arial", 30), fill=couleur_texte)

        # la valeur en bas a droite (retournee)
        canvas.create_text(62, 100, text=c["valeur"], font=("Arial", 13, "bold"), fill=couleur_texte)



def rafraichir():
    # on efface les anciennes cartes du croupier
    for widget in frame_cartes_croupier.winfo_children():
        widget.destroy()

    # on efface les anciennes cartes du joueur
    for widget in frame_cartes_joueur.winfo_children():
        widget.destroy()

    # on redessine les cartes du croupier
    for c in jeu["main_croupier"]:
        canvas = tk.Canvas(frame_cartes_croupier, width=80, height=120, bg=VERT, highlightthickness=0)
        canvas.pack(side="left", padx=5)
        dessiner_carte(canvas, c)

    # on redessine les cartes du joueur
    for c in jeu["main_joueur"]:
        canvas = tk.Canvas(frame_cartes_joueur, width=80, height=120, bg=VERT, highlightthickness=0)
        canvas.pack(side="left", padx=5)
        dessiner_carte(canvas, c)

    # on met a jour les scores
    label_score_croupier.config(text="croupier  -  score : " + str(score_visible_croupier(jeu)))
    label_score_joueur.config(text="joueur  -  score : " + str(score_main(jeu["main_joueur"])))

    # on active ou desactive les boutons selon letat du jeu
    if jeu["etat"] == "joue":
        btn_carte.config(state="normal", bg="#4caf50")
        btn_rester.config(state="normal", bg="#2196f3")
        btn_double.config(state="normal", bg="#ff9800")
        btn_abandonner.config(state="normal", bg="#f44336")
        label_resultat.config(text="")
    else:
        # partie finie : on desactive tout et on affiche le resultat
        btn_carte.config(state="disabled", bg=GRIS)
        btn_rester.config(state="disabled", bg=GRIS)
        btn_double.config(state="disabled", bg=GRIS)
        btn_abandonner.config(state="disabled", bg=GRIS)
        label_resultat.config(text=jeu["resultat"])


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

def clic_nouvelle_partie():
    nouvelle_partie(jeu)
    rafraichir()


#Parties de linteface

# titre en haut
label_titre = tk.Label(fenetre, text="BLACKJACK", font=("Arial", 28, "bold"), bg=VERT_FONCE, fg=JAUNE)
label_titre.pack(pady=10)

# zone croupier
frame_croupier = tk.Frame(fenetre, bg=VERT, padx=15, pady=10)
frame_croupier.pack(fill="x", padx=20, pady=5)

label_score_croupier = tk.Label(frame_croupier, text="croupier  -  score : 0", font=("Arial", 13), bg=VERT, fg=BLANC)
label_score_croupier.pack(anchor="w")

frame_cartes_croupier = tk.Frame(frame_croupier, bg=VERT)
frame_cartes_croupier.pack(pady=8)

# separateur
tk.Frame(fenetre, bg=VERT_FONCE, height=3).pack(fill="x", padx=20)

# zone joueur
frame_joueur = tk.Frame(fenetre, bg=VERT, padx=15, pady=10)
frame_joueur.pack(fill="x", padx=20, pady=5)

label_score_joueur = tk.Label(frame_joueur, text="joueur  -  score : 0", font=("Arial", 13), bg=VERT, fg=BLANC)
label_score_joueur.pack(anchor="w")

frame_cartes_joueur = tk.Frame(frame_joueur, bg=VERT)
frame_cartes_joueur.pack(pady=8)

# label resultat (vide pendant la partie)
label_resultat = tk.Label(fenetre, text="", font=("Arial", 22, "bold"), bg=VERT_FONCE, fg=JAUNE)
label_resultat.pack(pady=5)

# les boutons d action
frame_boutons = tk.Frame(fenetre, bg=VERT_FONCE)
frame_boutons.pack(pady=10)

btn_carte = tk.Button(frame_boutons, text="Carte", font=("Arial", 13, "bold"), width=10, fg=BLANC, relief="flat", command=clic_carte)
btn_carte.grid(row=0, column=0, padx=8, pady=5)

btn_rester = tk.Button(frame_boutons, text="Rester", font=("Arial", 13, "bold"), width=10, fg=BLANC, relief="flat", command=clic_rester)
btn_rester.grid(row=0, column=1, padx=8, pady=5)

btn_double = tk.Button(frame_boutons, text="Double", font=("Arial", 13, "bold"), width=10, fg=BLANC, relief="flat", command=clic_double)
btn_double.grid(row=0, column=2, padx=8, pady=5)

btn_abandonner = tk.Button(frame_boutons, text="Abandonner", font=("Arial", 13, "bold"), width=10, fg=BLANC, relief="flat", command=clic_abandonner)
btn_abandonner.grid(row=0, column=3, padx=8, pady=5)

# bouton nouvelle partie
btn_nouvelle = tk.Button(fenetre, text="Nouvelle partie", font=("Arial", 13, "bold"), bg=JAUNE, fg=NOIR, relief="flat", command=clic_nouvelle_partie)
btn_nouvelle.pack(pady=12)




nouvelle_partie(jeu)
rafraichir()
fenetre.mainloop()



#a rajouter: mise, multijoueur, interface graphique, sauvegarde des scores, split



