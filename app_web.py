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

# --- CHARGEMENT SÉCURISÉ ---
def charger_donnees():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and len(data) > 0:
                    return data
        except Exception:
            pass
    
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

# --- IMAGE DE FOND ---
def ajouter_image_fond(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded_string}");
                background-attachment: fixed;
                background-size: cover;
            }}
            .stApp > header {{ background-color: transparent; }}
            
            h1, h2, h3, h4, h5, h6, p, label, span, .stMarkdown, 
            div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] {{
                color: #FFFFFF !important;
                text-shadow: 2px 2px 5px #000000, -2px -2px 5px #000000, 2px -2px 5px #000000, -2px 2px 5px #000000 !important;
                font-weight: 800 !important;
            }}
            
            div[data-testid="stForm"], 
            div[data-testid="stExpander"], 
            div[data-testid="stMetric"] {{
                background-color: rgba(10, 10, 15, 0.8) !important;
                padding: 18px !important;
                border-radius: 12px !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
            }}

            section[data-testid="stSidebar"] {{
                background-color: rgba(15, 15, 20, 0.88) !important;
            }}

            div[data-testid="stTable"], div[data-testid="stDataFrame"] {{
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-radius: 8px !important;
            }}
            
            div[data-testid="stTable"] *, div[data-testid="stDataFrame"] * {{
                color: #000000 !important;
                text-shadow: none !important;
                font-weight: normal !important;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
        except Exception:
            pass

ajouter_image_fond(IMAGE_FOND_PATH)

# --- ENTÊTE ---
st.title("✨ DAHIRA NOUROU DARAYNI")
st.caption("Plateforme web globale — Gestion multi-cellules")

donnees = st.session_state.donnees

# --- ESPACE DE CONNEXION ---
col_cell, col_secu = st.columns([2, 1])

with col_cell:
    cellules = list(donnees.keys()) if donnees else CELLULES_PAR_DEFAUT
    cellule_selected = st.selectbox("📍 Sélectionner la Cellule :", cellules)
    
    if st.session_state.role_actif == "SUPER_ADMIN":
        with st.expander("+ Ajouter une nouvelle cellule (Super Admin)"):
            nouvelle_cellule = st.text_input("Nom de la nouvelle cellule")
            if st.button("Créer la cellule") and nouvelle_cellule:
                nom_clean = f"Section {nouvelle_cellule.replace('Section', '').strip()}"
                if nom_clean not in donnees:
                    donnees[nom_clean] = {"Membres Simples": [], "Cotisations": []}
                    for comm in COMMISSIONS_LISTE:
                        donnees[nom_clean][comm] = []
                    sauvegarder_donnees(donnees)
                    st.success(f"Cellule {nom_clean} créée !")
                    st.rerun()

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

    tot_membres = len(cell_data.get("Membres Simples", []))
    for k, v in cell_data.items():
        if k not in ["Membres Simples", "Cotisations"]:
            tot_membres += len(v)

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Membres", tot_membres)
    col2.metric("📋 Commissions", len([k for k in cell_data.keys() if k not in ["Membres Simples", "Cotisations"]]))

    somme = sum(c.get("montant", 0) for c in cell_data.get("Cotisations", []))
    col3.metric("💳 Total Cotisations", f"{somme:,.0f} FCFA")

    st.subheader("Derniers Membres Inscrits")
    membres_recents = cell_data.get("Membres Simples", [])[-5:]
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
    else:
        st.info("🔒 Saisissez le code de la Commission Administrative ou du Super Admin pour modifier.")

    membres = cell_data.get("Membres Simples", [])
    if membres:
        st.dataframe(membres, use_container_width=True)

        if peut_gerer_membres:
            with st.expander("🗑️ Supprimer un membre du registre"):
                options_membres = [f"{i} - {m['nom']} ({m.get('tel', 'Pas de tél')})" for i, m in enumerate(membres)]
                membre_a_suppr = st.selectbox("Sélectionner le membre à retirer :", options_membres)
                
                if st.button("❌ Supprimer définitivement ce membre", type="primary"):
                    idx = int(membre_a_suppr.split(" - ")[0])
                    nom_retire = membres[idx]['nom']
                    membres.pop(idx)
                    sauvegarder_donnees(donnees)
                    st.success(f"Le membre {nom_retire} a été supprimé !")
                    st.rerun()
    else:
        st.info("Aucun membre dans le registre de cette cellule.")

# --- PAGE COMMISSIONS ---
elif menu == "📋 Commissions":
    st.header(f"Gestion des Commissions — {cellule_selected}")

    commissions = [k for k in cell_data.keys() if k not in ["Membres Simples", "Cotisations"]]
    comm_selected = st.selectbox("Choisir une commission :", commissions) if commissions else None

    if comm_selected:
        peut_gerer_comm = a_permission(comm_selected)

        if peut_gerer_comm:
            with st.expander(f"➕ Affecter un membre à : {comm_selected}"):
                with st.form("form_comm"):
                    nom = st.text_input("Nom et Prénom")
                    tel = st.text_input("Téléphone")
                    btn_comm = st.form_submit_button("Affecter")

                    if btn_comm and nom:
                        cell_data.setdefault(comm_selected, []).append({"nom": nom.strip(), "tel": tel.strip()})
                        sauvegarder_donnees(donnees)
                        st.success("Affectation réussie !")
                        st.rerun()
        else:
            st.info(f"🔒 Saisissez le code secret dédié à la '{comm_selected}' pour modifier.")

        membres_comm = cell_data.get(comm_selected, [])
        if membres_comm:
            st.table(membres_comm)

            if peut_gerer_comm:
                with st.expander(f"🗑️ Retirer un membre de : {comm_selected}"):
                    opts_comm = [f"{i} - {m['nom']}" for i, m in enumerate(membres_comm)]
                    m_comm_suppr = st.selectbox("Sélectionner le membre à retirer :", opts_comm)
                    if st.button("❌ Retirer de la commission"):
                        idx_c = int(m_comm_suppr.split(" - ")[0])
                        membres_comm.pop(idx_c)
                        sauvegarder_donnees(donnees)
                        st.success("Membre retiré !")
                        st.rerun()
        else:
            st.info("Aucun membre affecté à cette commission.")

# --- PAGE COTISATIONS ---
elif menu == "💳 Cotisations":
    st.header(f"Cotisations — {cellule_selected}")

    peut_gerer_finance = a_permission("Commission Finance")

    if peut_gerer_finance:
        membres_liste = [m.get("nom") for comm, mm in cell_data.items() if comm != "Cotisations" for m in mm if m.get("nom")]

        with st.form("form_cotis"):
            st.subheader("Enregistrer un versement")
            m_select = st.selectbox("Sélectionner le membre :", sorted(list(set(membres_liste)))) if membres_liste else None
            mois_select = st.selectbox("Mois :", MOIS_ANNEE)
            montant = st.number_input("Montant (FCFA) :", min_value=0, step=500)
            btn_cotis = st.form_submit_button("Valider le versement")

            if btn_cotis and m_select and montant > 0:
                cell_data.setdefault("Cotisations", []).append({
                    "membre": m_select,
                    "mois": mois_select,
                    "montant": montant,
                    "date": datetime.now().strftime("%d/%m/%Y à %H:%M")
                })
                sauvegarder_donnees(donnees)
                st.success("Cotisation enregistrée avec succès !")
                st.rerun()
    else:
        st.info("🔒 Entrez le code secret de la Commission Finance (ou Super Admin) pour gérer les versements.")

    st.subheader("Historique des versements")
    cotisations = cell_data.get("Cotisations", [])
    if cotisations:
        st.dataframe(list(reversed(cotisations)), use_container_width=True)
        
        if peut_gerer_finance:
            with st.expander("🗑️ Supprimer une cotisation"):
                options_cotis = [f"{i} - {c['membre']} | {c['mois']} | {c['montant']} FCFA | ({c.get('date', '')})" for i, c in enumerate(cotisations)]
                cotis_a_supprimer = st.selectbox("Sélectionner la cotisation à effacer :", options_cotis)
                
                if st.button("❌ Effacer cette cotisation", type="primary"):
                    index_to_remove = int(cotis_a_supprimer.split(" - ")[0])
                    cotisations.pop(index_to_remove)
                    sauvegarder_donnees(donnees)
                    st.success("Cotisation effacée !")
                    st.rerun()
    else:
        st.info("Aucune cotisation enregistrée.")
