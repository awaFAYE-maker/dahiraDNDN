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

# --- CHARGEMENT DES DONNÉES ---
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
        background-color: rgba(0, 0, 0, 0.55);
        z-index: 0;
    }}

    h1, h2, h3, h4, h5, h6, p, label, span, div, li {{
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9) !important;
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
        background-color: rgba(15, 23, 42, 0.85) !important;
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

    tot_membres = len(cell_data.get("Membres Simples", [])) if isinstance(cell_data, dict) else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Membres", tot_membres)
    col2.metric("📋 Commissions", len(COMMISSIONS_LISTE))

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

    peut_gerer_membres = a_permission(besoin_admin_general=True)

    if peut_gerer_membres:
        col_add, col_del = st.columns(2)

        with col_add:
            with st.expander("➕ Inscrire un nouveau membre"):
                with st.form("form_membre"):
                    nom = st.text_input("Nom et Prénom")
                    tel = st.text_input("Téléphone")
                    btn_add = st.form_submit_button("Enregistrer le membre")

                    if btn_add and nom:
                        cell_data.setdefault("Membres Simples", []).append({"nom": nom.strip(), "tel": tel.strip()})
                        sauvegarder_donnees(donnees)
                        st.success(f"Membre {nom} ajouté !")
                        st.rerun()

        with col_del:
            with st.expander("🗑️ Supprimer un membre"):
                membres_existants = cell_data.get("Membres Simples", [])
                noms_membres = [m["nom"] for m in membres_existants] if membres_existants else []

                if noms_membres:
                    membre_a_supprimer = st.selectbox("Sélectionnez le membre à supprimer :", noms_membres)
                    if st.button("Confirmer la suppression", type="primary"):
                        cell_data["Membres Simples"] = [m for m in membres_existants if m["nom"] != membre_a_supprimer]
                        sauvegarder_donnees(donnees)
                        st.success(f"Membre {membre_a_supprimer} supprimé !")
                        st.rerun()
                else:
                    st.info("Aucun membre à supprimer.")

    membres = cell_data.get("Membres Simples", []) if isinstance(cell_data, dict) else []
    if membres:
        st.dataframe(membres, use_container_width=True)
    else:
        st.info("Aucun membre dans le registre de cette cellule.")

# --- PAGE COMMISSIONS ---
elif menu == "📋 Commissions":
    st.header(f"Gestion des Commissions — {cellule_selected}")

    comm_selected = st.selectbox("Choisir une commission :", COMMISSIONS_LISTE)

    peut_gerer_comm = a_permission(comm_selected) or a_permission(besoin_admin_general=True)

    if comm_selected:
        cell_data.setdefault(comm_selected, [])
        membres_comm = cell_data.get(comm_selected, [])

        if peut_gerer_comm:
            col_c1, col_c2 = st.columns(2)

            with col_c1:
                with st.expander(f"➕ Ajouter un membre dans : {comm_selected}"):
                    membres_dispos = [m for m in cell_data.get("Membres Simples", []) if m not in membres_comm]
                    noms_dispos = [m["nom"] for m in membres_dispos]

                    if noms_dispos:
                        nom_choisi = st.selectbox("Sélectionner un membre du registre :", noms_dispos)
                        if st.button("Ajouter à la commission"):
                            membre_obj = next(m for m in membres_dispos if m["nom"] == nom_choisi)
                            cell_data[comm_selected].append(membre_obj)
                            sauvegarder_donnees(donnees)
                            st.success(f"{nom_choisi} ajouté à {comm_selected} !")
                            st.rerun()
                    else:
                        st.info("Tous les membres sont déjà affectés ou aucun membre dans la cellule.")

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
            st.table(membres_comm)
        else:
            st.info("Aucun membre affecté à cette commission pour l'instant.")

# --- PAGE COTISATIONS (EXCLUSIF COMMISSION FINANCE & SUPER_ADMIN) ---
elif menu == "💳 Cotisations":
    st.header(f"Cotisations — {cellule_selected}")

    est_finance_ou_admin = a_permission("Commission Finance") or a_permission(besoin_admin_general=True)

    if not est_finance_ou_admin:
        st.error("🔒 Accès restreint. Seule la Commission Finance et le SUPER_ADMIN peuvent accéder aux cotisations.")
    else:
        with st.expander("➕ Enregistrer une nouvelle cotisation"):
            membres_cell = [m["nom"] for m in cell_data.get("Membres Simples", [])]
            if membres_cell:
                with st.form("form_cotisation"):
                    nom_payeur = st.selectbox("Membre :", membres_cell)
                    montant = st.number_input("Montant (FCFA) :", min_value=1000, step=500)
                    mois = st.selectbox("Mois :", MOIS_ANNEE)
                    btn_cotis = st.form_submit_button("Enregistrer la cotisation")

                    if btn_cotis:
                        cell_data.setdefault("Cotisations", []).append({
                            "membre": nom_payeur,
                            "montant": montant,
                            "mois": mois,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        sauvegarder_donnees(donnees)
                        st.success("Cotisation enregistrée avec succès !")
                        st.rerun()
            else:
                st.info("Veuillez d'abord enregistrer des membres dans cette cellule.")

        cotisations = cell_data.get("Cotisations", []) if isinstance(cell_data, dict) else []
        if cotisations:
            st.dataframe(list(reversed(cotisations)), use_container_width=True)
        else:
            st.info("Aucune cotisation enregistrée.")
