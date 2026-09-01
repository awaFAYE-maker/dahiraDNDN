"""
Script d'insertion des nouveaux membres — DAHIRA NOUROU DARAYNI, Section Dakar
--------------------------------------------------------------------------
À placer dans le même dossier que cellules.json (le dépôt dahiraDNDN),
puis lancer une seule fois :

    python inserer_membres_dakar.py

Le script ajoute les membres à "Section Dakar" -> "Membres Simples".
Si un membre du même nom existe déjà, il n'est pas ajouté en double.
"""

import json
import os

JSON_FILE = "cellules.json"
CELLULE_CIBLE = "Section Dakar"

# --- Nouveaux membres à insérer ---
NOUVEAUX_MEMBRES = [
    # Hommes
    {"nom": "Diawriñ Ousseynou Faye", "tel": "768825540"},
    {"nom": "S Saliou Gning", "tel": "761229780"},
    {"nom": "S Chérif Gning", "tel": "760275936"},
    {"nom": "S Ousseynou Gning", "tel": "700038103"},
    {"nom": "S Moustapha Gning", "tel": "778597661"},
    {"nom": "Adama Sene", "tel": "N/A"},
    {"nom": "Daouda Ngom", "tel": "782214569"},
    {"nom": "Saliou Faye", "tel": "705211296"},
    {"nom": "Ousmane Dieng", "tel": "772046703"},
    {"nom": "Moussa Ngom", "tel": "N/A"},
    {"nom": "Saliou Tine", "tel": "779026791"},
    {"nom": "Assane Faye", "tel": "705591656"},
    {"nom": "S Modou Sarr Dione", "tel": "763987453"},
    {"nom": "S Alioune Sene", "tel": "755291678"},
    {"nom": "Mamadou Séne", "tel": "761395175"},
    {"nom": "S Abdoulaye Sene", "tel": "771815022"},
    {"nom": "Ablaye Ndour Bayfall", "tel": "770403137"},
    {"nom": "Ibrahima Faye", "tel": "785629226"},
    {"nom": "Cheikh Ahmeth Tidiane Sonko", "tel": "770771944"},
    {"nom": "Cheikh Faye", "tel": "766051595"},
    {"nom": "Moussa Gning", "tel": "770841954"},
    {"nom": "S Saliou Sene", "tel": "784061939"},
    {"nom": "Elhadji Modou Dione", "tel": "779478083"},
    {"nom": "Modou Tine", "tel": "773680272"},
    {"nom": "Daouda Sene", "tel": "785126815"},
    {"nom": "Mohameth Sarr", "tel": "781607962"},
    {"nom": "Yoro Faye", "tel": "786149358"},
    {"nom": "Ousseynou Gning", "tel": "774192300"},
    {"nom": "Khadim Sene", "tel": "764447397"},
    {"nom": "Moustapha Gning", "tel": "762357412"},
    {"nom": "Ibra Dione", "tel": "764381888"},
    {"nom": "Abdou Diouf", "tel": "779510627"},
    {"nom": "Mamadou Gning", "tel": "770370075"},
    # Soxna yii (femmes)
    {"nom": "S Awa Faye", "tel": "774201453"},
    {"nom": "S Coumba Ngom", "tel": "765964478"},
    {"nom": "S Bineta Gning", "tel": "764534986"},
    {"nom": "S Niania Gning", "tel": "765849391"},
    {"nom": "S Astou Mbène Faye", "tel": "762078865"},
    {"nom": "Mareme Soda Tine", "tel": "779200585"},
    {"nom": "Amy Faye", "tel": "763201230"},
]


def charger():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauvegarder(donnees):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)


def main():
    donnees = charger()

    if CELLULE_CIBLE not in donnees:
        print(f"⚠️  '{CELLULE_CIBLE}' introuvable dans {JSON_FILE}. "
              f"Vérifiez le nom exact de la cellule ou lancez d'abord l'app une fois.")
        return

    cell_data = donnees[CELLULE_CIBLE]
    membres_simples = cell_data.setdefault("Membres Simples", [])
    noms_existants = {m.get("nom", "").strip().lower() for m in membres_simples if isinstance(m, dict)}

    ajoutes = 0
    deja_presents = 0

    for m in NOUVEAUX_MEMBRES:
        nom_clean = m["nom"].strip()
        if nom_clean.lower() in noms_existants:
            deja_presents += 1
            continue

        membres_simples.append({
            "nom": nom_clean,
            "tel": m["tel"],
            "adresse": "N/A",
            "profession": "N/A",
        })
        noms_existants.add(nom_clean.lower())
        ajoutes += 1

    sauvegarder(donnees)

    print(f"✅ {ajoutes} nouveau(x) membre(s) ajouté(s) à '{CELLULE_CIBLE}'.")
    if deja_presents:
        print(f"ℹ️  {deja_presents} membre(s) déjà présent(s) — ignoré(s) (pas de doublon).")


if __name__ == "__main__":
    main()
