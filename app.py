from flask import Flask, request, redirect, url_for, render_template, make_response
from weasyprint import HTML, CSS
from db import get_db_connection
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numero = request.form.get("numero_facture")
        if numero:
            return redirect(url_for("afficher_facture", numero=numero))
    return render_template("index.html")


@app.route("/facture")
def afficher_facture():
    numero = request.args.get("numero")
    if not numero:
        return "Numéro de facture manquant", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # ✅ Curseur en mode dictionnaire

    cursor.execute("""
        SELECT f.numero, f.date_facture, f.camion, f.remorque,
               f.description, f.ligne_depart, f.ligne_destination, f.montant, f.montant_lettres,
               f.tva, f.montant_ttc, f.devise,
               c.nom_societe, c.ice, c.adresse
        FROM facture f
        JOIN client c ON f.client_id = c.id
        WHERE f.numero = %s
    """, (numero,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return "Facture non trouvée", 404

    css_path = url_for('static', filename='style.css')
    logo_path = url_for('static', filename='logo.png')

    return render_template("factuAV.html", facture=row, css_path=css_path, logo_path=logo_path)


@app.route("/facture/pdf")
def telecharger_pdf():
    numero = request.args.get("numero")
    if not numero:
        return "Numéro de facture manquant", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # ✅ Curseur en mode dictionnaire

    cursor.execute("""
        SELECT f.numero, f.date_facture, f.camion, f.remorque,
               f.description, f.ligne_depart, f.ligne_destination, f.montant, f.montant_lettres,
               f.tva, f.montant_ttc, f.devise,
               c.nom_societe, c.ice, c.adresse
        FROM facture f
        JOIN client c ON f.client_id = c.id
        WHERE f.numero = %s
    """, (numero,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return "Facture non trouvée", 404

    html = render_template("factuAV.html",
                           facture=row,
                           css_path=url_for('static', filename='style.css', _external=True),
                           logo_path=url_for('static', filename='logo.png', _external=True))

    css_file = os.path.join(app.root_path, 'static', 'style.css')

    pdf = HTML(string=html, base_url=request.host_url).write_pdf(stylesheets=[CSS(css_file)])

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=facture_{numero}.pdf'
    return response
