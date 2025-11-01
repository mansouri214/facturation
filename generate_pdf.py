import pdfkit
from flask import Flask, send_file, make_response, render_template
import mysql.connector

app = Flask(__name__)

# Connexion à la base de données
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Remplace par ton mot de passe MySQL
    database="facturation"
)

@app.route("/facture/<int:id>/pdf")
def generate_pdf(id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM facture WHERE id = %s", (id,))
    row = cursor.fetchone()
    
    if not row:
        return "Facture non trouvée", 404

    facture = {
        "numero": row[1],
        "date": row[2],
        "camion": row[3],
        "remorque": row[4],
        "description": row[5],
        "trajet": row[6],
        "montant": row[7],
        "tva": row[8],
        "montant_ttc": row[9],
        "montant_lettres": row[10]
    }

    html = render_template("facture.html", facture=facture)

    # Générer le PDF (assure-toi que wkhtmltopdf est bien installé)
    pdf = pdfkit.from_string(html, False)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=facture_{facture['numero']}.pdf'
    return response

if __name__ == "__main__":
    app.run(debug=True)
