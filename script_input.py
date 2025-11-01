from num2words import num2words
from decimal import Decimal, ROUND_HALF_UP
from db import get_db_connection

# Connexion à la base de données
conn = get_db_connection()
cursor = conn.cursor()

# --- Saisie des données de la facture ---
numero = input("Numéro de la facture (x/xx): ")
date_facture = input("Date (YYYY-MM-DD) : ")
camion = input("Matricule du Camion : ")
remorque = input("Matricule de la Remorque : ")
description = input("Description du transport : ")
ligne_depart = input("La ligne de départ est : ")
ligne_destination = input("La ligne d'arrivée est : ")
montant = float(input("Montant du trajet HT : "))
tva_pourcentage = float(input("TVA (%) : "))
devise = input("Devise (MAD / EUR / USD) : ").upper()

# --- Informations du client ---
print("\n Informations du client :")
nom_societe = input("Nom de la société : ")
ice = input("ICE : ")
adresse = input("Adresse : ")
email = input("Email : ")
telephone = input("Téléphone : ")
type_client = input("Type de client : ")
# --- Calculs de montant TTC ---
montant_decimal = Decimal(str(montant))
tva_decimal = Decimal(str(tva_pourcentage)) / Decimal(100)
montant_ttc = (montant_decimal * (1 + tva_decimal)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

dirhams, centimes_str = str(montant_ttc).split('.')
dirhams = int(dirhams)
centimes = int(centimes_str)

# --- Conversion en lettres ---
devise_texte = {"MAD": "DIRHAM", "EUR": "EURO", "USD": "DOLLAR"}
devise_centime = {"MAD": "CENTIME", "EUR": "CENTIME", "USD": "CENT"}

monnaie = devise_texte.get(devise, "DIRHAM")
centime = devise_centime.get(devise, "CENTIME")

lettres_dirhams = num2words(dirhams, lang='fr').upper()
lettres_dirhams += f" {monnaie}" + ("S" if dirhams > 1 else "")

lettres_centimes = ""
if centimes > 0:
    lettres_centimes = num2words(centimes, lang='fr').upper()
    lettres_centimes += f" {centime}" + ("S" if centimes > 1 else "")
    montant_lettres = f"{lettres_dirhams} ET {lettres_centimes}"
else:
    montant_lettres = lettres_dirhams

# --- Insertion client ---
client_query = """
INSERT INTO client (nom_societe, ice, adresse, email, telephone, type)
VALUES (%s, %s, %s, %s, %s, %s)
"""
client_values = (nom_societe, ice, adresse, email, telephone, type_client)
cursor.execute(client_query, client_values)
client_id = cursor.lastrowid  #  Récupère l'ID du client inséré

# --- Insertion facture ---
facture_query = """
INSERT INTO facture (
    numero, date_facture, camion, remorque,
    description, ligne_depart, ligne_destination, montant, tva, montant_ttc,
    montant_lettres, devise, client_id
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
facture_values = (
    numero, date_facture, camion, remorque, description,
    ligne_depart, ligne_destination, float(montant_decimal), float(tva_pourcentage),
    float(montant_ttc), montant_lettres, devise, client_id
)

cursor.execute(facture_query, facture_values)
conn.commit()

# --- Résumé ---
print("\n✅ Facture enregistrée avec succès :")
print(f"Numéro : {numero}")
print(f"Date : {date_facture}")
print(f"Société : {nom_societe}")
print(f"Montant TTC : {montant_ttc} {devise}")
print(f"Montant en lettres : {montant_lettres}")

# --- Fermeture ---
cursor.close()
conn.close()
