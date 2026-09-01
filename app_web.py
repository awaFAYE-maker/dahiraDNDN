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
    st.subheader("📢 2. Envoi groupé rapide")

    if membres_avec_tel:
        # Extrait tous les numéros séparés par des virgules
        numeros_groupes = ", ".join([f"+{nettoyer_numero(m['tel'])}" for m in membres_avec_tel])
        
        st.write("📋 **Liste complète des numéros (pour Liste de Diffusion WhatsApp) :**")
        st.code(numeros_groupes, language="text")
        st.info("💡 **Astuce :** Copiez ces numéros ou le message ci-dessus, puis créez une **'Nouvelle Diffusion'** dans votre application WhatsApp sur téléphone.")

        st.divider()
        st.subheader("🔗 3. Liens d'envoi individuel rapide en 1-clic")
        st.caption("Cliquez sur chaque bouton pour ouvrir directement la discussion WhatsApp pré-remplie :")

        texte_encode = urllib.parse.quote(message_personnalise)

        # Affichage sous forme de grille de boutons d'envoi rapide
        col_m1, col_m2 = st.columns(2)
        for i, m in enumerate(membres_avec_tel):
            num_wa = nettoyer_numero(m["tel"])
            lien_wa = f"https://wa.me/{num_wa}?text={texte_encode}"
            col_target = col_m1 if i % 2 == 0 else col_m2
            
            with col_target:
                col_target.markdown(
                    f'''
                    <div style="background-color: rgba(255, 255, 255, 0.1); padding: 8px; border-radius: 6px; margin-bottom: 8px;">
                        <b>{m['nom']}</b> ({m['tel']})<br/>
                        <a href="{lien_wa}" target="_blank" style="background-color: #25D366; color: white; padding: 4px 10px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold;">📲 Envoyer sur WhatsApp</a>
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )
    else:
        st.warning("Aucun membre n'a de numéro valide renseigné.")
