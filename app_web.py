import streamlit as st
import json
import os
import base64
import csv
import io
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="DAHIRA NOUROU DARAYNI",
    page_icon="✨",
    layout="wide"
)

JSON_FILE = "cellules.json"
IMAGE_FOND_PATH = "AhmaduBamba.jpg"
DOSSIER_ARCHIVES = "archives_documents"

# Création du dossier d'archivage s'il n'existe pas
if not os.path.exists(DOSSIER_ARCHIVES):
    os.makedirs(DOSSIER_ARCHIVES)

# --- 🔑 RÔLES / COMMISSIONS ET CODES D'ACCÈS ---
CODES_COMMISSIONS = {
    "SUPER_ADMIN": "JARAJEUF BOROM TOUBA",
    "Commission Administrative": "SNDINDI",
    "Commission Organisation / Zikrulah": "JALIBATOU",
    "Commission Culturelle": "JAZBOU",
    "Commission Finance": "MAWAHIBOU"
}

CODE_ARCHIVES_SECRET = "ARCHIVES.DOC.DNDN"  # Code d'accès dédié aux archives si pas SUPER_ADMIN

COMMISSIONS_LISTE = list(CODES_COMMISSIONS.keys())[1:]
MOIS_ANNEE = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
EVENEMENTS_DEFAUT = ["Mensualité", "Ziar", "Ndogou"]

CELLULES_INITIALES = {
    "Section Dakar": "DKR.DNDN",
    "Section Saint-Louis": "STL.DNDN",
    "Section Ngoundiane": "NGOUNDIANE.DNDN",
    "Section Thiès": "THIES.DNDN",
    "Section Bambey": "BAMBEY.DNDN"
}

# --- TEXTES POUR LA PAGE À PROPOS ---
TEXTE_DAHIRA = """
Une **dahira** est une association religieuse mouride qui regroupe des talibés (disciples) autour
de la pratique du dhikr, des enseignements soufis et de l'organisation collective de la vie
communautaire : cotisations, entraide sociale, participation aux grands événements religieux
(Magal, Gamou, Ziarra) et soutien mutuel entre membres. C'est à la fois un lieu de spiritualité
et un espace de solidarité et d'organisation sociale.

La **Dahira Nourou Darayni** s'inscrit dans cette tradition : elle réunit ses membres autour des
enseignements de Cheikh Ahmadou Bamba, organise ses commissions (Administrative, Organisation /
Zikrulah, Culturelle, Finance) et gère la vie collective de ses différentes sections à travers le
Sénégal.
"""

TEXTE_CHEIKH_AHMADOU_BAMBA = """
Né vers 1853 à Mbacké, dans le Baol (Sénégal), **Cheikh Ahmadou Bamba Mbacké** est le fondateur
de la confrérie mouride, l'un des plus grands mouvements soufis d'Afrique de l'Ouest.

Il a prôné le travail et la prière comme voies complémentaires vers Dieu, résumées dans la
formule du **Khidma** (le service par le travail). Face à son influence grandissante, l'administration
coloniale française l'exila à plusieurs reprises, notamment au Gabon puis en Mauritanie.

Il fonda la ville sainte de **Touba**, aujourd'hui le principal centre spirituel du mouridisme, où se
tient chaque année le **Grand Magal** commémorant son premier exil. Son enseignement continue de
structurer la vie de millions de disciples à travers les dahiras, au Sénégal comme dans la diaspora.
"""

TEXTE_CHEIKH_IBRA_FALL = """
**Mame Cheikh Ibra Fall (1858–1930)** fut le tout premier disciple de Cheikh Ahmadou Bamba et
son plus fidèle serviteur. Il est le fondateur de la voie des **Baye Fall**, une branche du
mouridisme fondée sur la soumission totale au maître et le **travail (Khidma)** érigé en acte
d'adoration à part entière, en complément — et parfois à la place — des piliers rituels classiques.

Les Baye Fall se reconnaissent traditionnellement à leurs habits rapiécés colorés (le **mbubb**),
symbole d'humilité et de détachement des biens matériels, et à leur dévouement inlassable au
service de la communauté : construction, agriculture, organisation des grands événements
religieux. Ils incarnent l'idée que le travail accompli avec sincérité et pour la communauté est
une forme de prière.
"""

TEXTE_PERSPECTIVES = """
Une dahira ne se limite pas à la collecte des cotisations : c'est aussi un espace vivant qui peut
grandir autour de nouveaux projets. Quelques pistes qui inspirent souvent les dahiras aujourd'hui :

- **Cours de Coran et d'arabe** pour les enfants et les nouveaux talibés
- **Caisse de solidarité** pour les événements heureux (mariages, naissances) et les épreuves (maladie, deuil)
- **Organisation de Gamou et Ziarra** vers Touba et les autres lieux saints
- **Formation professionnelle** des jeunes membres (artisanat, numérique, agriculture)
- **Bibliothèque numérique** des Xassidas (poèmes) de Cheikh Ahmadou Bamba
- **Sensibilisation et santé communautaire** en lien avec les commissions locales
"""

# --- CHARGEMENT DES DONNÉES ---
def charger_donnees():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                donnees = json.load(f)
                for cell, pwd in CELLULES_INITIALES.items():
                    if cell in donnees:
                        if "code_acces" not in donnees[cell]:
                            donnees[cell]["code_acces"] = pwd
                        if "Evenements" not in donnees[cell]:
                            donnees[cell]["Evenements"] = EVENEMENTS_DEFAUT.copy()
                        if "Archives" not in donnees[cell]:
                            donnees[cell]["Archives"] = []
                return donnees
        except Exception as e:
            st.error(f"⚠️ Erreur de lecture du fichier : {e}")

    structure = {}
    for cell, pwd in CELLULES_INITIALES.items():
        structure[cell] = {
            "code_acces": pwd,
            "Membres Simples": [],
            "Cotisations": [],
            "Evenements": EVENEMENTS_DEFAUT.copy(),
            "Archives": []
        }
        for comm in COMMISSIONS_LISTE:
            structure[cell][comm] = []
    return structure


def sauvegarder_donnees(donnees):
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")


if "donnees" not in st.session_state:
    st.session_state.donnees = charger_donnees()

if "cellules_deverouillees" not in st.session_state:
    st.session_state.cellules_deverouillees = []

if "role_actif" not in st.session_state:
    st.session_state.role_actif = None

if "archives_deverouillees" not in st.session_state:
    st.session_state.archives_deverouillees = False

# --- IMAGE DE FOND ET STYLE CSS ---
bg_css = ""
if os.path.exists(IMAGE_FOND_PATH):
    try:
        with open(IMAGE_FOND_PATH, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            bg_css = f'background-image: url("data:image/png;base64,{encoded_string}");'
    except Exception:
        pass

st.markdown(
    f"""
    <style>
    .stApp {{
        {bg_css}
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}

    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.68);
        z-index: 0;
    }}

    h1, h2, h3, h4, h5, h6, p, label, span, div, li {{
        color: #FFFFFF !important;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.9) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: #FFFFFF !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.9) !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: #F0F0F0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(8px);
    }}

    .stAlert {{
        background-color: rgba(0, 0, 0, 0.65) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
    }}

    .stTextInput input, .stSelectbox div, .stNumberInput input {{
        color: #000000 !important;
        text-shadow: none !important;
    }}

    .carte-apropos {{
        background-color: rgba(15, 23, 42, 0.55);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- ENTÊTE ---
st.title("✨ DAHIRA NOUROU DARAYNI")
st.caption("Plateforme web globale — Gestion multi-cellules sécurisée")

donnees = st.session_state.donnees
role = st.session_state.role_actif

# --- AUTHENTIFICATION ---
col_cell, col_secu = st.columns([2, 1])

with col_cell:
    cellules_dispos = list(donnees.keys())
    cellule_selected = st.selectbox("📍 Sélectionner votre Cellule :", cellules_dispos)

    if role == "SUPER_ADMIN":
        with st.expander("➕ Ajouter une nouvelle cellule (SUPER ADMIN)"):
            with st.form("form_nouvelle_cellule"):
                nom_nouvelle_cell = st.text_input("Nom de la cellule (ex: Section Louga) :")
                code_nouvelle_cell = st.text_input("Code d'accès secret pour cette cellule :", type="password")
                btn_creer_cell = st.form_submit_button("Créer la cellule")

                if btn_creer_cell and nom_nouvelle_cell and code_nouvelle_cell:
                    nom_clean = nom_nouvelle_cell.strip()
                    if nom_clean in donnees:
                        st.error("⚠️ Cette cellule existe déjà !")
                    else:
                        donnees[nom_clean] = {
                            "code_acces": code_nouvelle_cell.strip(),
                            "Membres Simples": [],
                            "Cotisations": [],
                            "Evenements": EVENEMENTS_DEFAUT.copy(),
                            "Archives": []
                        }
                        for comm in COMMISSIONS_LISTE:
                            donnees[nom_clean][comm] = []

                        sauvegarder_donnees(donnees)
                        st.success(f"✅ La cellule '{nom_clean}' a été créée avec son code d'accès !")
                        st.rerun()

with col_secu:
    st.write("**🔑 Authentification Commission / Admin**")
    if role is None:
        pwd_role = st.text_input("Code rôle/commission :", type="password", key="pwd_login")
        if st.button("🔓 S'authentifier"):
            role_trouve = None
            for r, code in CODES_COMMISSIONS.items():
                if pwd_role == code:
                    role_trouve = r
                    break

            if role_trouve:
                st.session_state.role_actif = role_trouve
                st.success(f"Connecté : {role_trouve}")
                st.rerun()
            else:
                st.error("Code rôle incorrect !")
    else:
        st.success(f"🟢 Actif : **{st.session_state.role_actif}**")
        if st.button("🔒 Déconnexion Rôle"):
            st.session_state.role_actif = None
            st.rerun()

st.divider()

# --- VÉRIFICATION D'ACCÈS CELLULE ---
cell_data = donnees.get(cellule_selected, {})
code_cellule_attendu = cell_data.get("code_acces", "TOUBA_2026")

est_super_admin = (role == "SUPER_ADMIN")
cellule_deverouillee = (cellule_selected in st.session_state.cellules_deverouillees) or est_super_admin

if not cellule_deverouillee:
    st.warning(f"🔒 L'accès à la **{cellule_selected}** est protégé. Veuillez saisir le code d'accès de cette cellule pour continuer.")
    with st.form("form_acces_cellule"):
        pwd_cell_saisi = st.text_input(f"Code d'accès secret de la {cellule_selected} :", type="password")
        btn_valider_cell = st.form_submit_button("Déverrouiller la cellule")

        if btn_valider_cell:
            if pwd_cell_saisi == code_cellule_attendu:
                st.session_state.cellules_deverouillees.append(cellule_selected)
                st.success(f"Bienvenue dans la {cellule_selected} !")
                st.rerun()
            else:
                st.error("❌ Code d'accès de la cellule incorrect !")
    st.stop()

# --- PERMISSIONS ---
def peut_gerer_membres_global():
    return role in ["SUPER_ADMIN", "Commission Administrative", "Commission Finance"]


def a_permission(nom_commission=None):
    if role == "SUPER_ADMIN":
        return True
    if nom_commission and role == nom_commission:
        return True
    return False


def obtenir_tous_les_membres_uniques(c_data):
    tous_membres = []
    noms_vus = set()

    for m in c_data.get("Membres Simples", []):
        if isinstance(m, dict) and m.get("nom") and m["nom"] not in noms_vus:
            tous_membres.append(m)
            noms_vus.add(m["nom"])

    for comm in COMMISSIONS_LISTE:
        for m in c_data.get(comm, []):
            if isinstance(m, dict) and m.get("nom") and m["nom"] not in noms_vus:
                tous_membres.append(m)
                noms_vus.add(m["nom"])

    return tous_membres


def cotisations_vers_csv(liste_cotisations):
    """Convertit une liste de cotisations en texte CSV téléchargeable."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Membre", "Événement", "Montant (FCFA)", "Mois", "Date d'enregistrement"])
    for c in liste_cotisations:
        writer.writerow([c.get("membre", ""), c.get("evenement", ""), c.get("montant", 0), c.get("mois", ""), c.get("date", "")])
    return buffer.getvalue().encode("utf-8-sig")


def stats_globales(toutes_les_donnees):
    """Calcule les statistiques agrégées sur l'ensemble des cellules (toutes sections)."""
    nb_membres_total = 0
    nb_cotisations_total = 0
    montant_total = 0
    for c_data in toutes_les_donnees.values():
        nb_membres_total += len(obtenir_tous_les_membres_uniques(c_data))
        cotis = c_data.get("Cotisations", [])
        nb_cotisations_total += len(cotis)
        montant_total += sum(c.get("montant", 0) for c in cotis)
    return {
        "nb_sections": len(toutes_les_donnees),
        "nb_membres_total": nb_membres_total,
        "nb_cotisations_total": nb_cotisations_total,
        "montant_total": montant_total,
    }


# --- NAVIGATION ---
menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "👥 Membres", "📋 Commissions", "💳 Cotisations", "📁 Archivage Documents", "ℹ️ À propos"]
)

# --- ACCUEIL ---
if menu == "🏠 Accueil":
    st.markdown(
        "<div class='carte-apropos'>"
        "<p style='letter-spacing:2px; font-size:0.85rem; opacity:0.85;'>—— DAHIRA NOUROU DARAYNI</p>"
        f"<h2 style='margin-top:0;'>Bienvenue, {cellule_selected}</h2>"
        "<p>Gérez vos membres, vos commissions, vos cotisations et vos archives depuis un seul espace, "
        "au service de la dahira et dans l'esprit de Cheikh Ahmadou Bamba.</p>"
        "</div>",
        unsafe_allow_html=True
    )

    membres_uniques = obtenir_tous_les_membres_uniques(cell_data)
    stats_g = stats_globales(donnees)

    st.subheader(f"Tableau de Bord — {cellule_selected}")
    col1, col2 = st.columns(2)
    col1.metric("👥 Total Membres (Cellule)", len(membres_uniques))
    col2.metric("📋 Commissions", len(COMMISSIONS_LISTE))

    with st.expander("🌍 Vue d'ensemble — toutes les sections de la Dahira"):
        cg1, cg2 = st.columns(2)
        cg1.metric("🏘️ Sections actives", stats_g["nb_sections"])
        cg2.metric("👥 Membres (toutes sections)", stats_g["nb_membres_total"])
        st.caption("💡 Le détail des cotisations est réservé à la Commission Finance (page Cotisations).")

    st.divider()

    col_evt, col_marche = st.columns(2)

    with col_evt:
        st.subheader("🎪 Événements de la cellule")
        evenements_cell_accueil = cell_data.get("Evenements", EVENEMENTS_DEFAUT.copy())
        if evenements_cell_accueil:
            for evt in evenements_cell_accueil:
                st.markdown(f"- {evt}")
        else:
            st.info("Aucun événement enregistré pour l'instant.")
        st.caption("💳 Cotisations acceptées via Wave, Orange Money ou en espèces auprès de la Commission Finance.")

    with col_marche:
        st.subheader("📌 Comment ça marche")
        st.markdown(
            "**1. Rejoindre la dahira** — Se rapprocher de la Commission Administrative de sa section.\n\n"
            "**2. Être enregistré** — Vos informations (nom, contact, profession) sont ajoutées au registre des membres.\n\n"
            "**3. Cotiser régulièrement** — Mensualités et cotisations d'événements enregistrées et suivies dans l'application."
        )

    st.divider()
    st.subheader("Derniers Membres Inscrits")
    membres_recents = membres_uniques[-5:]
    if membres_recents:
        st.table(membres_recents)
    else:
        st.info(f"Aucun membre enregistré pour la {cellule_selected}.")

    st.divider()
    st.subheader("🌟 Nos valeurs")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        st.markdown("**🤲 Khidma**")
        st.caption("Le service et le travail comme voie de rapprochement avec Dieu.")
    with v2:
        st.markdown("**🕌 Zikrulah**")
        st.caption("La pratique régulière du dhikr et des enseignements soufis.")
    with v3:
        st.markdown("**🤝 Entraide**")
        st.caption("La solidarité entre membres, dans la joie comme dans l'épreuve.")
    with v4:
        st.markdown("**📚 Transmission**")
        st.caption("Le partage des enseignements de Cheikh Ahmadou Bamba aux générations futures.")

# --- MEMBRES ---
elif menu == "👥 Membres":
    st.header(f"Registre des Membres — {cellule_selected}")

    if peut_gerer_membres_global():
        col_add, col_del = st.columns(2)

        with col_add:
            with st.expander("➕ Inscrire un nouveau membre"):
                with st.form("form_membre"):
                    nom = st.text_input("Nom et Prénom *")
                    tel = st.text_input("Téléphone")
                    adresse = st.text_input("Adresse / Quartier")
                    profession = st.text_input("Fonction / Profession (ex: Électricien, Maçon...)")
                    btn_add = st.form_submit_button("Enregistrer le membre")

                    if btn_add and nom:
                        nouveau_membre = {
                            "nom": nom.strip(),
                            "tel": tel.strip() if tel else "N/A",
                            "adresse": adresse.strip() if adresse else "N/A",
                            "profession": profession.strip() if profession else "N/A"
                        }
                        cell_data.setdefault("Membres Simples", []).append(nouveau_membre)
                        sauvegarder_donnees(donnees)
                        st.success(f"Membre {nom} ajouté à la {cellule_selected} !")
                        st.rerun()

        with col_del:
            with st.expander("🗑️ Supprimer un membre"):
                membres_existants = cell_data.get("Membres Simples", [])
                noms_membres = [m["nom"] for m in membres_existants] if membres_existants else []

                if noms_membres:
                    membre_a_supprimer = st.selectbox("Sélectionnez le membre à supprimer :", noms_membres)
                    if st.button("Confirmer la suppression", type="primary"):
                        cell_data["Membres Simples"] = [m for m in membres_existants if m["nom"] != membre_a_supprimer]
                        for comm in COMMISSIONS_LISTE:
                            cell_data[comm] = [m for m in cell_data.get(comm, []) if m.get("nom") != membre_a_supprimer]

                        sauvegarder_donnees(donnees)
                        st.success(f"Membre {membre_a_supprimer} supprimé de la cellule !")
                        st.rerun()
                else:
                    st.info("Aucun membre à supprimer.")
    else:
        st.info("ℹ️ Mode lecture seule. Seules les Commissions Administrative et Finance peuvent inscrire ou supprimer des membres.")

    st.subheader(f"🔍 Recherche & Liste générale des membres ({cellule_selected})")

    recherche = st.text_input("🔎 Rechercher par métier/profession, nom ou adresse (ex: electricien, étudiant) :", key="search_bar")
    membres_totaux = obtenir_tous_les_membres_uniques(cell_data)

    if recherche.strip():
        terme = recherche.strip().lower()
        membres_filtres = [
            m for m in membres_totaux
            if terme in m.get("profession", "").lower()
            or terme in m.get("nom", "").lower()
            or terme in m.get("adresse", "").lower()
        ]

        st.success(f"🎯 **{len(membres_filtres)}** membre(s) trouvé(s) pour la recherche « **{recherche}** »")
        if membres_filtres:
            st.dataframe(membres_filtres, use_container_width=True)
        else:
            st.warning("Aucun membre ne correspond à cette recherche.")
    else:
        if membres_totaux:
            st.dataframe(membres_totaux, use_container_width=True)
        else:
            st.info(f"Aucun membre enregistré dans la {cellule_selected}.")

# --- COMMISSIONS ---
elif menu == "📋 Commissions":
    st.header(f"Gestion des Commissions — {cellule_selected}")

    comm_selected = st.selectbox("Choisir une commission :", COMMISSIONS_LISTE)
    peut_gerer_comm = peut_gerer_membres_global() or a_permission(comm_selected)

    if comm_selected:
        cell_data.setdefault(comm_selected, [])
        membres_comm = cell_data.get(comm_selected, [])

        if peut_gerer_comm:
            col_c1, col_c2 = st.columns(2)

            with col_c1:
                with st.expander(f"➕ Ajouter un membre dans : {comm_selected}"):
                    type_ajout = st.radio("Méthode d'ajout :", ["Sélectionner depuis le registre", "Créer un nouveau membre complet"], key="type_ajout_comm")

                    if type_ajout == "Sélectionner depuis le registre":
                        membres_dispos = [m for m in cell_data.get("Membres Simples", []) if m not in membres_comm]
                        noms_dispos = [m["nom"] for m in membres_dispos]

                        if noms_dispos:
                            nom_choisi = st.selectbox("Sélectionner un membre :", noms_dispos)
                            if st.button("Ajouter à la commission"):
                                membre_obj = next(m for m in membres_dispos if m["nom"] == nom_choisi)
                                cell_data[comm_selected].append(membre_obj)
                                sauvegarder_donnees(donnees)
                                st.success(f"{nom_choisi} ajouté à {comm_selected} !")
                                st.rerun()
                        else:
                            st.info("Tous les membres du registre sont déjà dans cette commission ou le registre est vide.")

                    else:
                        with st.form("form_nouveau_membre_comm"):
                            nouveau_nom = st.text_input("Nom et Prénom *")
                            nouveau_tel = st.text_input("Téléphone")
                            nouvelle_adresse = st.text_input("Adresse / Quartier")
                            nouvelle_prof = st.text_input("Fonction / Profession")
                            btn_creer = st.form_submit_button("Créer et ajouter à la commission")

                            if btn_creer and nouveau_nom:
                                nouveau_membre = {
                                    "nom": nouveau_nom.strip(),
                                    "tel": nouveau_tel.strip() if nouveau_tel else "N/A",
                                    "adresse": nouvelle_adresse.strip() if nouvelle_adresse else "N/A",
                                    "profession": nouvelle_prof.strip() if nouvelle_prof else "N/A"
                                }
                                cell_data[comm_selected].append(nouveau_membre)
                                if nouveau_membre not in cell_data.get("Membres Simples", []):
                                    cell_data.setdefault("Membres Simples", []).append(nouveau_membre)

                                sauvegarder_donnees(donnees)
                                st.success(f"{nouveau_nom} créé et ajouté à {comm_selected} !")
                                st.rerun()

            with col_c2:
                with st.expander(f"🗑️ Retirer un membre de : {comm_selected}"):
                    noms_dans_comm = [m["nom"] for m in membres_comm]
                    if noms_dans_comm:
                        nom_retrait = st.selectbox("Sélectionner le membre à retirer :", noms_dans_comm)
                        if st.button("Retirer de la commission"):
                            cell_data[comm_selected] = [m for m in membres_comm if m["nom"] != nom_retrait]
                            sauvegarder_donnees(donnees)
                            st.success(f"{nom_retrait} retiré de {comm_selected} !")
                            st.rerun()
                    else:
                        st.info("Aucun membre dans cette commission.")

        st.subheader(f"Membres affectés à : {comm_selected}")
        if membres_comm:
            st.dataframe(membres_comm, use_container_width=True)
        else:
            st.info("Aucun membre affecté à cette commission pour l'instant.")

# --- COTISATIONS ---
elif menu == "💳 Cotisations":
    st.header(f"Cotisations — {cellule_selected}")

    est_finance_ou_admin = a_permission("Commission Finance") or role == "SUPER_ADMIN"

    if not est_finance_ou_admin:
        st.error("🔒 Accès restreint. Seule la Commission Finance et le SUPER_ADMIN peuvent accéder aux cotisations.")
    else:
        evenements_cell = cell_data.setdefault("Evenements", EVENEMENTS_DEFAUT.copy())

        col_cotis_add, col_evt = st.columns(2)

        with col_cotis_add:
            with st.expander("➕ Enregistrer une nouvelle cotisation"):
                st.caption("💳 Moyens de paiement acceptés : Wave · Orange Money · Espèces")
                membres_totaux = [m["nom"] for m in obtenir_tous_les_membres_uniques(cell_data)]
                if membres_totaux:
                    with st.form("form_cotisation"):
                        nom_payeur = st.selectbox("Membre :", membres_totaux)
                        type_evt = st.selectbox("Type de cotisation / Événement :", evenements_cell)
                        montant = st.number_input("Montant (FCFA) :", min_value=1000, step=500)
                        mois = st.selectbox("Mois :", MOIS_ANNEE)
                        btn_cotis = st.form_submit_button("Enregistrer la cotisation")

                        if btn_cotis:
                            cell_data.setdefault("Cotisations", []).append({
                                "membre": nom_payeur,
                                "evenement": type_evt,
                                "montant": montant,
                                "mois": mois,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                            sauvegarder_donnees(donnees)
                            st.success(f"Cotisation pour {type_evt} enregistrée avec succès !")
                            st.rerun()
                else:
                    st.info("Veuillez d'abord enregistrer des membres dans cette cellule.")

        with col_evt:
            with st.expander("🎪 Ajouter un nouvel événement (Gamou, Chantier...)"):
                with st.form("form_nouvel_evenement"):
                    nom_evt = st.text_input("Nom du nouvel événement :")
                    btn_add_evt = st.form_submit_button("Ajouter l'événement")

                    if btn_add_evt and nom_evt:
                        evt_clean = nom_evt.strip()
                        if evt_clean in evenements_cell:
                            st.warning("Cet événement existe déjà !")
                        else:
                            evenements_cell.append(evt_clean)
                            sauvegarder_donnees(donnees)
                            st.success(f"✅ Événement '{evt_clean}' ajouté !")
                            st.rerun()

            with st.expander("🗑️ Supprimer une cotisation"):
                cotisations_liste = cell_data.get("Cotisations", [])
                if cotisations_liste:
                    options_cotis = [
                        f"{c['membre']} — {c.get('evenement', 'Cotisation')} : {c['montant']:,.0f} FCFA ({c['mois']})"
                        for c in cotisations_liste
                    ]
                    cotis_choisie = st.selectbox("Sélectionner la cotisation à supprimer :", options_cotis)

                    if st.button("Supprimer cette cotisation", type="primary"):
                        idx = options_cotis.index(cotis_choisie)
                        cotisation_retiree = cell_data["Cotisations"].pop(idx)
                        sauvegarder_donnees(donnees)
                        st.success(f"Cotisation de {cotisation_retiree['membre']} supprimée !")
                        st.rerun()
                else:
                    st.info("Aucune cotisation enregistrée à supprimer.")

        st.divider()
        st.subheader(f"📊 Historique et Bilan des Cotisations ({cellule_selected})")

        cotisations = cell_data.get("Cotisations", []) if isinstance(cell_data, dict) else []

        if cotisations:
            filtre_evt = st.selectbox("Filtrer l'historique par événement :", ["Tous les événements"] + evenements_cell)

            if filtre_evt != "Tous les événements":
                cotis_affichees = [c for c in cotisations if c.get("evenement") == filtre_evt]
            else:
                cotis_affichees = cotisations

            total_collecte = sum(c["montant"] for c in cotis_affichees)
            col_total, col_export = st.columns([3, 1])
            col_total.metric(f"💰 Total Collecté ({filtre_evt})", f"{total_collecte:,.0f} FCFA")
            with col_export:
                st.write("")
                st.download_button(
                    "📤 Exporter en CSV",
                    data=cotisations_vers_csv(cotis_affichees),
                    file_name=f"cotisations_{cellule_selected.replace(' ', '_')}.csv",
                    mime="text/csv"
                )

            # Évolution des montants collectés par mois
            totaux_par_mois = {mois_nom: 0 for mois_nom in MOIS_ANNEE}
            for c in cotis_affichees:
                if c.get("mois") in totaux_par_mois:
                    totaux_par_mois[c["mois"]] += c["montant"]
            st.caption("Évolution des montants collectés par mois")
            st.bar_chart(totaux_par_mois)

            st.dataframe(list(reversed(cotis_affichees)), use_container_width=True)
        else:
            st.info("Aucune cotisation enregistrée pour le moment.")

# --- ARCHIVAGE DOCUMENTS (RÉSERVÉ SUPER ADMIN OU CODE ARCHIVES) ---
elif menu == "📁 Archivage Documents":
    st.header(f"Coffre-fort Documents & Archives — {cellule_selected}")

    est_autorise = est_super_admin or st.session_state.archives_deverouillees

    if not est_autorise:
        st.warning("🔒 L'accès au coffre-fort d'archivage est restreint. Veuillez saisir le code d'accès des archives ou vous connecter en SUPER_ADMIN.")
        with st.form("form_acces_archives"):
            code_saisi = st.text_input("Code d'accès secret aux archives :", type="password")
            btn_unlock_archives = st.form_submit_button("Déverrouiller les archives")

            if btn_unlock_archives:
                if code_saisi == CODE_ARCHIVES_SECRET:
                    st.session_state.archives_deverouillees = True
                    st.success("Accès aux archives accordé !")
                    st.rerun()
                else:
                    st.error("❌ Code secret incorrect !")
        st.stop()

    # SECTION UNE FOIS AUTORISÉ
    col_upload, col_stat = st.columns([2, 1])

    archives_cellule = cell_data.setdefault("Archives", [])

    with col_upload:
        with st.expander("📤 Archiver un nouveau document"):
            fichier_uploade = st.file_uploader("Sélectionner un fichier (PDF, Word, Excel, Image...)", type=None)
            description_doc = st.text_input("Description / Objet du document :")

            if st.button("Sauvegarder dans les archives"):
                if fichier_uploade is not None:
                    nom_fichier = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fichier_uploade.name}"
                    chemin_sauvegarde = os.path.join(DOSSIER_ARCHIVES, nom_fichier)

                    with open(chemin_sauvegarde, "wb") as f:
                        f.write(fichier_uploade.getbuffer())

                    doc_info = {
                        "nom_original": fichier_uploade.name,
                        "nom_stocke": nom_fichier,
                        "description": description_doc if description_doc else "Aucune description",
                        "taille_ko": round(len(fichier_uploade.getbuffer()) / 1024, 2),
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }

                    archives_cellule.append(doc_info)
                    sauvegarder_donnees(donnees)
                    st.success(f"Document '{fichier_uploade.name}' archivé avec succès !")
                    st.rerun()
                else:
                    st.error("Veuillez sélectionner un fichier avant d'enregistrer.")

    with col_stat:
        st.metric("📁 Documents Archivés", len(archives_cellule))

    st.divider()
    st.subheader(f"📑 Liste des documents archivés ({cellule_selected})")

    if archives_cellule:
        for idx, doc in enumerate(reversed(archives_cellule)):
            chemin_doc = os.path.join(DOSSIER_ARCHIVES, doc["nom_stocke"])
            col_doc1, col_doc2, col_doc3 = st.columns([3, 1, 1])

            with col_doc1:
                st.markdown(f"**📄 {doc['nom_original']}**")
                st.caption(f"📝 {doc['description']} | 📅 {doc['date']} | 💾 {doc['taille_ko']} KB")

            with col_doc2:
                if os.path.exists(chemin_doc):
                    with open(chemin_doc, "rb") as file_data:
                        st.download_button(
                            label="📥 Télécharger",
                            data=file_data,
                            file_name=doc['nom_original'],
                            key=f"dl_{idx}"
                        )
                else:
                    st.error("Fichier introuvable")

            with col_doc3:
                if st.button("🗑️ Supprimer", key=f"del_doc_{idx}"):
                    if os.path.exists(chemin_doc):
                        os.remove(chemin_doc)

                    real_idx = len(archives_cellule) - 1 - idx
                    archives_cellule.pop(real_idx)
                    sauvegarder_donnees(donnees)
                    st.success("Document supprimé !")
                    st.rerun()
            st.divider()
    else:
        st.info(f"Aucun document n'a encore été archivé pour la {cellule_selected}.")

# --- À PROPOS ---
elif menu == "ℹ️ À propos":
    st.header("À propos de la Dahira")

    st.markdown(f"<div class='carte-apropos'><h3>🕌 Qu'est-ce qu'une Dahira ?</h3>{TEXTE_DAHIRA}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='carte-apropos'><h3>📜 Cheikh Ahmadou Bamba (1853–1927)</h3>{TEXTE_CHEIKH_AHMADOU_BAMBA}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='carte-apropos'><h3>🧵 Mame Cheikh Ibra Fall et les Baye Fall</h3>{TEXTE_CHEIKH_IBRA_FALL}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='carte-apropos'><h3>🌱 Perspectives pour la Dahira</h3>{TEXTE_PERSPECTIVES}</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Nos Commissions")
    for comm in COMMISSIONS_LISTE:
        st.markdown(f"- **{comm}**")
