import streamlit as st
import json
import os
import base64
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="DAHIRA NOUROU DARAYNI",
    page_icon="✨",
    layout="wide"
)

JSON_FILE = "cellules.json"
IMAGE_FOND_PATH = "AhmaduBamba.jpg"

# --- 🔑 DICTIONNAIRE DES CODES SECRETS ---
CODES_SECRETS = {
    "SUPER_ADMIN": "TOUBA_ADMIN",
    "Commission Administrative": "ADMIN_2026",
    "Commission Organisation / Zikrulah": "ORGA_2026",
    "Commission Culturelle": "CULTURE_2026",
    "Commission Finance": "FINANCE_2026"
}

CELLULES_PAR_DEFAUT = ["Section Dakar", "Section Saint-Louis", "Section Ngoundiane", "Section Thiès", "Section Bambey"]
COMMISSIONS_LISTE = list(CODES_SECRETS.keys())[1:]
MOIS_ANNEE = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

# --- CHARGEMENT ultra-sécurisé ---
def charger_donnees():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            st.error(f"⚠️ Erreur de format dans cellules.json : {e}")
        except Exception as e:
            st.error(f"⚠️ Erreur de lecture du fichier : {e}")
            
    structure = {}
    for cell in CELLULES_PAR_DEFAUT:
        structure[cell] = {"Membres Simples": [], "Cotisations": []}
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

if "role_actif" not in st.session_state:
    st.session_state.role_actif = None

# --- IMAGE DE FOND ET STYLE CSS (TEXTES EN BLANC & LISIBILITÉ) ---
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
    /* Image de fond globale */
    .stApp {{
        {bg_css}
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}

    /* Voile sombre transparent pour améliorer le contraste */
    .stApp::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 0;
    }}

    /* Forcer la couleur blanche sur tous les textes */
    h1, h2, h3, h4, h5, h6, p, label, span, div, li {{
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }}

    /* Style spécifique pour les valeurs des métriques */
    [data-testid="stMetricValue"] {{
        color: #FFFFFF !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.9) !important;
    }}

    /* Style spécifique pour les libellés des métriques */
    [data-testid="stMetricLabel"] {{
        color: #F0F0F0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
    }}

    /* Fond semi-transparent pour la barre latérale */
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(8px);
    }}

    /* Boîtes d'alerte et messages d'information */
    .stAlert {{
        background-color: rgba(0, 0, 0, 0.65) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
    }}

    /* Champs de saisie (inputs) pour garder le texte lisible pendant la frappe */
    .stTextInput input, .stSelectbox div {{
        color: #000000 !important;
        text-shadow: none !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- ENTÊTE ---
st.title("✨ DAHIRA NOUROU DARAYNI")
st.caption("Plateforme web globale — Gestion multi-cellules")

donnees = st.session_state.donnees

# --- ESPACE DE CONNEXION ---
col_cell, col_secu = st.columns([2, 1])

with col_cell:
    cellules = list(donnees.keys()) if donnees else CELLULES_PAR_DEFAUT
    cellule_selected = st.selectbox("📍 Sélectionner la Cellule :", cellules)

with col_secu:
    st.write("**🔒 Authentification**")
    if st.session_state.role_actif is None:
        pwd = st.text_input("Entrez votre code secret :", type="password", key="pwd_login")
        if st.button("🔓 S'authentifier"):
            role_trouve = None
            for role, code in CODES_SECRETS.items():
                if pwd == code:
                    role_trouve = role
                    break
            
            if role_trouve:
                st.session_state.role_actif = role_trouve
                st.success(f"Connecté : {role_trouve}")
                st.rerun()
            else:
                st.error("Code secret incorrect !")
    else:
        st.success(f"🟢 Actif : **{st.session_state.role_actif}**")
        if st.button("🔒 Déconnexion"):
            st.session_state.role_actif = None
            st.rerun()

st.divider()

cell_data = donnees.get(cellule_selected, {})
role = st.session_state.role_actif

def a_permission(nom_commission=None, besoin_admin_general=False):
    if role == "SUPER_ADMIN":
        return True
    if besoin_admin_general and role == "Commission Administrative":
        return True
    if nom_commission and role == nom_commission:
        return True
    return False

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["🏠 Accueil", "👥 Membres", "📋 Commissions", "💳 Cotisations"])

# --- PAGE ACCUEIL ---
if menu == "🏠 Accueil":
    st.header(f"Tableau de Bord — {cellule_selected}")

    tot_membres = 0
    if isinstance(cell_data, dict):
        for k, v in cell_data.items():
            if isinstance(v, list):
                tot_membres += len(v)

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Membres", tot_membres)
    col2.metric("📋 Commissions", len([k for k in cell_data.keys() if k not in ["Membres Simples", "Cotisations"]]) if isinstance(cell_data, dict) else 0)

    cotis = cell_data.get("Cotisations", []) if isinstance(cell_data, dict) else []
    somme = sum(c.get("montant", 0) for c in cotis if isinstance(c, dict))
    col3.metric("💳 Total Cotisations", f"{somme:,.0f} FCFA")

    st.subheader("Derniers Membres Inscrits")
    membres_recents = cell_data.get("Membres Simples", [])[-5:] if isinstance(cell_data, dict) else []
    if membres_recents:
        st.table(membres_recents)
    else:
        st.info("Aucun membre enregistré dans cette cellule.")

# --- PAGE MEMBRES ---
elif menu == "👥 Membres":
    st.header(f"Registre des Membres — {cellule_selected}")

    peut_gerer_membres = a_permission(besoin_admin_general=True) or a_permission("Commission Administrative")

    if peut_gerer_membres:
        with st.expander("➕ Inscrire un nouveau membre dans cette cellule"):
            with st.form("form_membre"):
                nom = st.text_input("Nom et Prénom")
                tel = st.text_input("Téléphone")
                btn_add = st.form_submit_button("Enregistrer le membre")

                if btn_add and nom:
                    cell_data.setdefault("Membres Simples", []).append({"nom": nom.strip(), "tel": tel.strip()})
                    sauvegarder_donnees(donnees)
                    st.success(f"Membre {nom} ajouté !")
                    st.rerun()

    membres = cell_data.get("Membres Simples", []) if isinstance(cell_data, dict) else []
    if membres:
        st.dataframe(membres, use_container_width=True)
    else:
        st.info("Aucun membre dans le registre de cette cellule.")

# --- PAGE COMMISSIONS ---
elif menu == "📋 Commissions":
    st.header(f"Gestion des Commissions — {cellule_selected}")

    commissions = [k for k in cell_data.keys() if k not in ["Membres Simples", "Cotisations"]] if isinstance(cell_data, dict) else []
    comm_selected = st.selectbox("Choisir une commission :", commissions) if commissions else None

    if comm_selected:
        membres_comm = cell_data.get(comm_selected, [])
        if membres_comm:
            st.table(membres_comm)
        else:
            st.info("Aucun membre affecté à cette commission.")

# --- PAGE COTISATIONS ---
elif menu == "💳 Cotisations":
    st.header(f"Cotisations — {cellule_selected}")
    cotisations = cell_data.get("Cotisations", []) if isinstance(cell_data, dict) else []
    if cotisations:
        st.dataframe(list(reversed(cotisations)), use_container_width=True)
    else:
        st.info("Aucune cotisation enregistrée.")
