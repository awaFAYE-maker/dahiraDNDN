import streamlit as st
import json
import os
import base64
import urllib.parse
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

if not os.path.exists(DOSSIER_ARCHIVES):
    os.makedirs(DOSSIER_ARCHIVES)

# --- 🔑 RÔLES & CODES D'ACCÈS ---
CODES_COMMISSIONS = {
    "SUPER_ADMIN": "TOUBA_ADMIN",
    "Commission Administrative": "ADMIN_2026",
    "Commission Organisation / Zikrulah": "JALIBATOU",
    "Commission Culturelle": "CULTURE_2026",
    "Commission Finance": "FINANCE_2026"
}

CODE_ARCHIVES_SECRET = "ARCHIVES_2026"
COMMISSIONS_LISTE = list(CODES_COMMISSIONS.keys())[1:]
MOIS_ANNEE = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
EVENEMENTS_DEFAUT = ["Mensualité", "Ziar", "Ndogou"]

CELLULES_INITIALES = {
    "Section Dakar": "DAKAR_2026",
    "Section Saint-Louis": "STL_2026",
    "Section Ngoundiane": "NGOUNDIANE_2026",
    "Section Thiès": "THIES_2026",
    "Section Bambey": "BAMBEY_2026"
}

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
                        if "Evenements_A_Venir" not in donnees[cell]:
                            donnees[cell]["Evenements_A_Venir"] = []
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
            "Archives": [],
            "Evenements_A_Venir": []
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

# --- STYLE CSS & FOND ---
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
        top: 0; left: 0; width: 100%; height: 100%;
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
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(8px);
    }}
    .stTextInput input, .stSelectbox div, .stNumberInput input, .stTextArea textarea {{
        color: #000000 !important;
        text-shadow: none !important;
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
                nom_nouvelle_cell = st.text_input("Nom de la cellule :")
                code_nouvelle_cell = st.text_input("Code d'accès secret :", type="password")
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
                            "Archives": [],
                            "Evenements_A_Venir": []
                        }
                        for comm in COMMISSIONS_LISTE:
                            donnees[nom_clean][comm] = []
                        sauvegarder_donnees(donnees)
                        st.success(f"✅ Cellule '{nom_clean}' créée !")
                        st.rerun()

with col_secu:
    st.write("**🔑 Authentification Rôle**")
    if role is None:
        pwd_role = st.text_input("Code rôle/commission :", type="password", key="pwd_login")
        if st.button("🔓 S'authentifier"):
            role_trouve = next((r for r, code in CODES_COMMISSIONS.items() if pwd_role == code), None)
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

# --- VÉRIFICATION ACCÈS CELLULE ---
cell_data = donnees.get(cellule_selected, {})
code_cellule_attendu = cell_data.get("code_acces", "TOUBA_2026")
est_super_admin = (role == "SUPER_ADMIN")
cellule_deverouillee = (cellule_selected in st.session_state.cellules_deverouillees) or est_super_admin

if not cellule_deverouillee:
    st.warning(f"🔒 L'accès à la **{cellule_selected}** est protégé.")
    with st.form("form_acces_cellule"):
        pwd_cell_saisi = st.text_input(f"Code d'accès secret :", type="password")
        if st.form_submit_button("Déverrouiller"):
            if pwd_cell_saisi == code_cellule_attendu:
                st.session_state.cellules_deverouillees.append(cellule_selected)
                st.rerun()
            else:
                st.error("❌ Code incorrect !")
    st.stop()

# --- PERMISSIONS & UTILS ---
def peut_gerer_membres_global():
    return role in ["SUPER_ADMIN", "Commission Administrative", "Commission Finance"]

def a_permission(nom_commission=None):
    return (role == "SUPER_ADMIN") or (nom_commission and role == nom_commission)

def obtenir_tous_les_membres_uniques(c_data):
    tous_membres = []
    noms_vus = set()
    for key in ["Membres Simples"] + COMMISSIONS_LISTE:
        for m in c_data.get(key, []):
            if isinstance(m, dict) and m.get("nom") and m["nom"] not in noms_vus:
                tous_membres.append(m)
                noms_vus.add(m["nom"])
    return tous_membres

def nettoyer_numero(tel):
    if not tel or tel == "N/A":
        return None
    clean = "".join(filter(str.isdigit, str(tel)))
    if len(clean) == 9 and clean.startswith(("70", "75", "76", "77", "78")):
        return f"221{clean}"
    elif len(clean) == 12 and clean.startswith("221"):
        return clean
    return None

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", [
    "🏠 Accueil", 
    "👥 Membres", 
    "✏️ Modifier / Gérer Membres",
    "📲 Rappels WhatsApp", 
    "📅 Événements à Venir",
    "📋 Commissions", 
    "💳 Cotisations", 
    "📁 Archivage Documents"
])

# --- 🏠 ACCUEIL ---
if menu == "🏠 Accueil":
    st.header(f"Tableau de Bord — {cellule_selected}")
    membres_uniques = obtenir_tous_les_membres_uniques(cell_data)

    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Total Membres", len(membres_uniques))
    c2.metric("📋 Commissions", len(COMMISSIONS_LISTE))
    c3.metric("📅 Événements à venir", len(cell_data.get("Evenements_A_Venir", [])))

    st.subheader("Derniers Membres Inscrits")
    st.table(membres_uniques[-5:] if membres_uniques else [])

# --- 👥 MEMBRES ---
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
                    profession = st.text_input("Fonction / Profession")
                    if st.form_submit_button("Enregistrer"):
                        if nom:
                            cell_data.setdefault("Membres Simples", []).append({
                                "nom": nom.strip(),
                                "tel": tel.strip() if tel else "N/A",
                                "adresse": adresse.strip() if adresse else "N/A",
                                "profession": profession.strip() if profession else "N/A"
                            })
                            sauvegarder_donnees(donnees)
                            st.success(f"Membre {nom} ajouté !")
                            st.rerun()

        with col_del:
            with st.expander("🗑️ Supprimer un membre"):
                membres_existants = cell_data.get("Membres Simples", [])
                noms_membres = [m["nom"] for m in membres_existants]
                if noms_membres:
                    membre_a_supprimer = st.selectbox("Sélectionnez le membre à supprimer :", noms_membres)
                    if st.button("Confirmer la suppression", type="primary"):
                        cell_data["Membres Simples"] = [m for m in membres_existants if m["nom"] != membre_a_supprimer]
                        for comm in COMMISSIONS_LISTE:
                            cell_data[comm] = [m for m in cell_data.get(comm, []) if m.get("nom") != membre_a_supprimer]
                        sauvegarder_donnees(donnees)
                        st.success(f"{membre_a_supprimer} supprimé !")
                        st.rerun()

    st.subheader("🔍 Recherche & Liste globale")
    recherche = st.text_input("🔎 Rechercher par métier, nom ou adresse :", key="search_bar")
    membres_totaux = obtenir_tous_les_membres_uniques(cell_data)

    if recherche.strip():
        terme = recherche.strip().lower()
        membres_filtres = [
            m for m in membres_totaux 
            if terme in m.get("profession", "").lower() 
            or terme in m.get("nom", "").lower() 
            or terme in m.get("adresse", "").lower()
        ]
        st.success(f"🎯 **{len(membres_filtres)}** membre(s) trouvé(s)")
        st.dataframe(membres_filtres, use_container_width=True)
    else:
        st.dataframe(membres_totaux, use_container_width=True)

# --- ✏️ MODIFIER / GÉRER MEMBRES ---
elif menu == "✏️ Modifier / Gérer Membres":
    st.header(f"✏️ Modification des Membres — {cellule_selected}")

    if not peut_gerer_membres_global():
        st.error("🔒 Seules les Commissions Administrative, Finance et le SUPER_ADMIN peuvent modifier les membres.")
    else:
        membres_totaux = obtenir_tous_les_membres_uniques(cell_data)
        if membres_totaux:
            noms_liste = [m["nom"] for m in membres_totaux]
            membre_choisi_nom = st.selectbox("Sélectionner le membre à modifier :", noms_liste)

            membre_obj = next(m for m in membres_totaux if m["nom"] == membre_choisi_nom)

            st.info(f"Modification de la fiche de : **{membre_obj['nom']}**")

            with st.form("form_edit_membre"):
                nouveau_nom = st.text_input("Nom et Prénom :", value=membre_obj.get("nom", ""))
                nouveau_tel = st.text_input("Téléphone :", value=membre_obj.get("tel", "N/A"))
                nouvelle_adresse = st.text_input("Adresse / Quartier :", value=membre_obj.get("adresse", "N/A"))
                nouvelle_prof = st.text_input("Profession / Métier :", value=membre_obj.get("profession", "N/A"))

                btn_sauver_edit = st.form_submit_button("💾 Enregistrer les modifications")

                if btn_sauver_edit:
                    ancien_nom = membre_obj["nom"]
                    membre_obj["nom"] = nouveau_nom.strip()
                    membre_obj["tel"] = nouveau_tel.strip() if nouveau_tel.strip() else "N/A"
                    membre_obj["adresse"] = nouvelle_adresse.strip() if nouvelle_adresse.strip() else "N/A"
                    membre_obj["profession"] = nouvelle_prof.strip() if nouvelle_prof.strip() else "N/A"

                    for key in ["Membres Simples"] + COMMISSIONS_LISTE:
                        for m in cell_data.get(key, []):
                            if m.get("nom") == ancien_nom:
                                m.update(membre_obj)

                    sauvegarder_donnees(donnees)
                    st.success(f"✅ Fiche de {nouveau_nom} mise à jour avec succès !")
                    st.rerun()
        else:
            st.info("Aucun membre enregistré.")

# --- 📲 RAPPELS WHATSAPP ---
elif menu == "📲 Rappels WhatsApp":
    st.header(f"📲 Centre de Diffusion WhatsApp — {cellule_selected}")
    membres_totaux = obtenir_tous_les_membres_uniques(cell_data)

    membres_avec_tel = [m for m in membres_totaux if nettoyer_numero(m.get("tel")) is not None]
    membres_sans_tel = [m for m in membres_totaux if nettoyer_numero(m.get("tel")) is None]

    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("📱 Membres joignables", len(membres_avec_tel))
    col_stat2.metric("⚠️ Membres sans numéro", len(membres_sans_tel))

    st.subheader("✍️ 1. Rédiger le message de groupe / diffusion")
    
    type_rappel = st.radio("Modèle de message rapide :", [
        "Personnalisé", 
        "Rappel Cotisation Mensuelle", 
        "Convocation Réunion Dahira"
    ])

    if type_rappel == "Rappel Cotisation Mensuelle":
        msg_defaut = f"Salam Alaykoum cher(e) membre du DAHIRA NOUROU DARAYNI ({cellule_selected}). Nous vous rappelons le paiement de votre cotisation mensuelle. Dieuredieufe!"
    elif type_rappel == "Convocation Réunion Dahira":
        msg_defaut = f"Salam Alaykoum. Vous êtes convoqué(e) à la prochaine réunion du DAHIRA NOUROU DARAYNI ({cellule_selected}). Présence vivement souhaitée. Dieuredieufe!"
    else:
        msg_defaut = "Salam Alaykoum cher membre du DAHIRA NOUROU DARAYNI..."

    message_personnalise = st.text_area("Texte du message à diffuser :", value=msg_defaut, height=120)

    st.divider()
    st.subheader("☑️ 2. Cocher les membres destinataires")

    if membres_avec_tel:
        tout_cocher = st.checkbox("✅ Sélectionner / Tout cocher", value=True)

        membres_selectionnes = []
        col_c1, col_c2 = st.columns(2)
        
        for i, m in enumerate(membres_avec_tel):
            col_target = col_c1 if i % 2 == 0 else col_c2
            est_coche = col_target.checkbox(f"{m['nom']} ({m['tel']})", value=tout_cocher, key=f"cb_m_{i}")
            if est_coche:
                membres_selectionnes.append(m)

        st.divider()
        st.subheader("📢 3. Liste de diffusion générée")

        if membres_selectionnes:
            numeros_selectionnes = ", ".join([f"+{nettoyer_numero(m['tel'])}" for m in membres_selectionnes])
            
            st.success(f"🎯 **{len(membres_selectionnes)} membre(s) coché(s)**")
            st.write("📋 **Liste des numéros des membres cochés (pour Liste de Diffusion WhatsApp) :**")
            st.code(numeros_selectionnes, language="text")
            
            st.info("💡 **Mode d'emploi pour envoyer à tous les cohés à la fois :** Copiez la liste de numéros ci-dessus. Sur votre téléphone, allez dans WhatsApp > **Nouvelle Diffusion**, collez la liste et envoyez votre message !")

            st.divider()
            st.subheader("🔗 Liens d'envoi rapide pour les membres cochés :")
            texte_encode = urllib.parse.quote(message_personnalise)

            col_m1, col_m2 = st.columns(2)
            for i, m in enumerate(membres_selectionnes):
                num_wa = nettoyer_numero(m["tel"])
                lien_wa = f"https://wa.me/{num_wa}?text={texte_encode}"
                col_target = col_m1 if i % 2 == 0 else col_m2
                
                with col_target:
                    col_target.markdown(
                        f'''
                        <div style="background-color: rgba(255, 255, 255, 0.1); padding: 8px; border-radius: 6px; margin-bottom: 8px;">
                            <b>{m['nom']}</b><br/>
                            <a href="{lien_wa}" target="_blank" style="background-color: #25D366; color: white; padding: 4px 10px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold;">📲 Envoyer sur WhatsApp</a>
                        </div>
                        ''', 
                        unsafe_allow_html=True
                    )
        else:
            st.warning("Veuillez cocher au moins un membre.")
    else:
        st.warning("Aucun membre n'a de numéro valide renseigné.")

# --- 📅 ÉVÉNEMENTS À VENIR ---
elif menu == "📅 Événements à Venir":
    st.header(f"📅 Événements & Cotisations à Venir — {cellule_selected}")

    events = cell_data.setdefault("Evenements_A_Venir", [])

    if peut_gerer_membres_global():
        with st.expander("➕ Programmer un nouvel événement à venir"):
            with st.form("form_event_venir"):
                titre_evt = st.text_input("Nom de l'événement (ex: Grand Ziar Touba, Gamou 2026...) :")
                date_evt = st.date_input("Date de l'événement :")
                montant_cible = st.number_input("Cotisation demandée par membre (FCFA) :", min_value=0, step=500, value=5000)
                description_evt = st.text_area("Description / Objectifs :")

                if st.form_submit_button("Enregistrer l'événement"):
                    if titre_evt:
                        events.append({
                            "titre": titre_evt.strip(),
                            "date": str(date_evt),
                            "montant_cible": montant_cible,
                            "description": description_evt.strip()
                        })
                        sauvegarder_donnees(donnees)
                        st.success(f"Événement '{titre_evt}' ajouté !")
                        st.rerun()

    st.subheader("📋 Liste des événements futurs")

    if events:
        for idx, evt in enumerate(events):
            col_e1, col_e2 = st.columns([3, 1])
            with col_e1:
                st.markdown(f"### 🎪 {evt['titre']}")
                st.markdown(f"📅 **Date :** {evt['date']} | 💰 **Cotisation fixée :** {evt['montant_cible']:,.0f} FCFA / membre")
                st.write(f"📝 {evt.get('description', '')}")

            with col_e2:
                if peut_gerer_membres_global():
                    if st.button("🗑️ Supprimer", key=f"del_evt_{idx}"):
                        events.pop(idx)
                        sauvegarder_donnees(donnees)
                        st.success("Événement supprimé !")
                        st.rerun()

            with st.expander(f"📲 Envoyer un rappel WhatsApp pour : {evt['titre']}"):
                membres_totaux = obtenir_tous_les_membres_uniques(cell_data)
                membres_avec_tel = [m for m in membres_totaux if nettoyer_numero(m.get("tel")) is not None]

                msg_evt = f"Salam Alaykoum ! Rappel pour l'événement '{evt['titre']}' prévu le {evt['date']}. La participation est fixée à {evt['montant_cible']:,.0f} FCFA. Dieuredieufe!"
                st.info(f"Message type : {msg_evt}")

                if membres_avec_tel:
                    m_dest = st.selectbox("Choisir le membre :", [m["nom"] for m in membres_avec_tel], key=f"sel_m_{idx}")
                    m_obj = next(m for m in membres_avec_tel if m["nom"] == m_dest)
                    num_wa = nettoyer_numero(m_obj["tel"])
                    url_wa = f"https://wa.me/{num_wa}?text={urllib.parse.quote(msg_evt)}"
                    
                    st.markdown(f'<a href="{url_wa}" target="_blank" style="background-color: #25D366; color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; font-weight: bold;">📲 Envoyer le rappel WhatsApp à {m_dest}</a>', unsafe_allow_html=True)

            st.divider()
    else:
        st.info("Aucun événement à venir programmé.")

# --- 📋 COMMISSIONS ---
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
                with st.expander(f"➕ Ajouter dans : {comm_selected}"):
                    membres_dispos = [m for m in cell_data.get("Membres Simples", []) if m not in membres_comm]
                    noms_dispos = [m["nom"] for m in membres_dispos]
                    if noms_dispos:
                        nom_choisi = st.selectbox("Sélectionner un membre :", noms_dispos)
                        if st.button("Ajouter à la commission"):
                            membre_obj = next(m for m in membres_dispos if m["nom"] == nom_choisi)
                            cell_data[comm_selected].append(membre_obj)
                            sauvegarder_donnees(donnees)
                            st.success(f"{nom_choisi} ajouté !")
                            st.rerun()
            with col_c2:
                with st.expander(f"🗑️ Retirer de : {comm_selected}"):
                    noms_dans_comm = [m["nom"] for m in membres_comm]
                    if noms_dans_comm:
                        nom_retrait = st.selectbox("Sélectionner :", noms_dans_comm)
                        if st.button("Retirer"):
                            cell_data[comm_selected] = [m for m in membres_comm if m["nom"] != nom_retrait]
                            sauvegarder_donnees(donnees)
                            st.success(f"{nom_retrait} retiré !")
                            st.rerun()

        st.subheader(f"Membres de : {comm_selected}")
        st.dataframe(membres_comm, use_container_width=True)

# --- 💳 COTISATIONS ---
elif menu == "💳 Cotisations":
    st.header(f"Cotisations — {cellule_selected}")
    if not (a_permission("Commission Finance") or est_super_admin):
        st.error("🔒 Seule la Commission Finance et le SUPER_ADMIN ont accès aux cotisations.")
    else:
        evenements_cell = cell_data.setdefault("Evenements", EVENEMENTS_DEFAUT.copy())
        col_cotis_add, col_evt = st.columns(2)

        with col_cotis_add:
            with st.expander("➕ Enregistrer une cotisation"):
                membres_totaux = [m["nom"] for m in obtenir_tous_les_membres_uniques(cell_data)]
                if membres_totaux:
                    with st.form("form_cotisation"):
                        nom_payeur = st.selectbox("Membre :", membres_totaux)
                        type_evt = st.selectbox("Événement / Type :", evenements_cell)
                        montant = st.number_input("Montant (FCFA) :", min_value=1000, step=500)
                        mois = st.selectbox("Mois :", MOIS_ANNEE)
                        if st.form_submit_button("Enregistrer"):
                            cell_data.setdefault("Cotisations", []).append({
                                "membre": nom_payeur,
                                "evenement": type_evt,
                                "montant": montant,
                                "mois": mois,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                            sauvegarder_donnees(donnees)
                            st.success("Cotisation enregistrée !")
                            st.rerun()

        with col_evt:
            with st.expander("🎪 Ajouter une catégorie d'événement"):
                with st.form("form_nouvel_evt"):
                    nom_evt = st.text_input("Nom de la catégorie :")
                    if st.form_submit_button("Ajouter") and nom_evt:
                        if nom_evt.strip() not in evenements_cell:
                            evenements_cell.append(nom_evt.strip())
                            sauvegarder_donnees(donnees)
                            st.success("Événement ajouté !")
                            st.rerun()

        st.divider()
        st.subheader(f"📊 Historique et Bilan ({cellule_selected})")
        cotisations = cell_data.get("Cotisations", [])
        if cotisations:
            filtre_evt = st.selectbox("Filtrer par événement :", ["Tous les événements"] + evenements_cell)
            cotis_affichees = cotisations if filtre_evt == "Tous les événements" else [c for c in cotisations if c.get("evenement") == filtre_evt]
            st.metric("💰 Total Collecté", f"{sum(c['montant'] for c in cotis_affichees):,.0f} FCFA")
            st.dataframe(list(reversed(cotis_affichees)), use_container_width=True)
        else:
            st.info("Aucune cotisation enregistrée.")

# --- 📁 ARCHIVAGE DOCUMENTS ---
elif menu == "📁 Archivage Documents":
    st.header(f"Coffre-fort Documents — {cellule_selected}")
    est_autorise = est_super_admin or st.session_state.archives_deverouillees

    if not est_autorise:
        st.warning("🔒 Saisissez le code d'accès aux archives.")
        with st.form("form_acces_archives"):
            code_saisi = st.text_input("Code archives :", type="password")
            if st.form_submit_button("Déverrouiller"):
                if code_saisi == CODE_ARCHIVES_SECRET:
                    st.session_state.archives_deverouillees = True
                    st.rerun()
                else:
                    st.error("❌ Code secret incorrect !")
        st.stop()

    archives_cellule = cell_data.setdefault("Archives", [])
    
    with st.expander("📤 Archiver un nouveau document"):
        fichier_uploade = st.file_uploader("Sélectionner un fichier (PDF, Word, Excel, Image...)", type=None)
        description_doc = st.text_input("Description :")
        if st.button("Sauvegarder"):
            if fichier_uploade is not None:
                nom_fichier = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fichier_uploade.name}"
                chemin_sauvegarde = os.path.join(DOSSIER_ARCHIVES, nom_fichier)

                with open(chemin_sauvegarde, "wb") as f:
                    f.write(fichier_uploade.getbuffer())

                archives_cellule.append({
                    "nom_original": fichier_uploade.name,
                    "nom_stocke": nom_fichier,
                    "description": description_doc if description_doc else "Aucune description",
                    "taille_ko": round(len(fichier_uploade.getbuffer()) / 1024, 2),
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                sauvegarder_donnees(donnees)
                st.success("Document archivé !")
                st.rerun()

    st.subheader(f"📑 Documents archivés ({cellule_selected})")
    if archives_cellule:
        for idx, doc in enumerate(reversed(archives_cellule)):
            chemin_doc = os.path.join(DOSSIER_ARCHIVES, doc["nom_stocke"])
            c_d1, c_d2, c_d3 = st.columns([3, 1, 1])
            with c_d1:
                st.markdown(f"**📄 {doc['nom_original']}**")
                st.caption(f"📝 {doc['description']} | 📅 {doc['date']} | 💾 {doc['taille_ko']} KB")
            with c_d2:
                if os.path.exists(chemin_doc):
                    with open(chemin_doc, "rb") as file_data:
                        st.download_button("📥 Télécharger", file_data, file_name=doc['nom_original'], key=f"dl_{idx}")
            with c_d3:
                if st.button("🗑️ Supprimer", key=f"del_doc_{idx}"):
                    if os.path.exists(chemin_doc):
                        os.remove(chemin_doc)
                    archives_cellule.pop(len(archives_cellule) - 1 - idx)
                    sauvegarder_donnees(donnees)
                    st.rerun()
            st.divider()
    else:
        st.info("Aucun document archivé.")
