from flask import Flask, send_file, render_template, request, redirect, flash, url_for, session, jsonify
from num2words import num2words
from db import get_db_connection
from weasyprint import HTML, CSS
from io import BytesIO
import os
from flask import jsonify
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, timedelta
app = Flask(__name__)
app.secret_key = 'ma_cle_super_secrete'
bcrypt = Bcrypt(app)

# Configuration de login pour securite
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Connexion requise", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Fonction pour convertir montant en lettres selon le devise
def convertir_en_lettres(montant, devise):
    devise_map = {
        'MAD': 'dirhams',
        'EUR': 'euros',
        'USD': 'dollars',
    }

    nom_devise = devise_map.get(devise.upper(), devise)
    entiers = int(montant)
    centimes = int(round((montant - entiers) * 100))

    mots = num2words(entiers, lang='fr').upper() + f" {nom_devise}".upper()
    if centimes > 0:
        mots += " ET " + num2words(centimes, lang='fr').upper() + " CENTIMES"
    return mots


# ============ ROUTES AJOUTER CLIENT =============
@app.route('/ajouter-client', methods=['GET'])
@login_required
def afficher_formulaire_client():
    return render_template('ajouter_client.html')


@app.route('/ajouter-client', methods=['POST'])
@login_required
def ajouter_client():
    try:
        nom_societe = request.form['nom_societe']
        ice = request.form['ice']
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        email = request.form['email']
        periode_echeance = int(request.form.get('periode_echeance', 30))

        conn = get_db_connection()
        cur = conn.cursor()

        # Vérifier chaque champ unique
        cur.execute("SELECT id FROM client WHERE nom_societe = %s", (nom_societe,))
        if cur.fetchone():
            flash("❌ Un client avec ce nom de société existe déjà.", "danger")
            return redirect(url_for('afficher_formulaire_client'))

        cur.execute("SELECT id FROM client WHERE ice = %s", (ice,))
        if cur.fetchone():
            flash("❌ Un client avec ce numéro ICE existe déjà.", "danger")
            return redirect(url_for('afficher_formulaire_client'))

        cur.execute("SELECT id FROM client WHERE telephone = %s", (telephone,))
        if cur.fetchone():
            flash("❌ Ce numéro de téléphone est déjà utilisé.", "danger")
            return redirect(url_for('afficher_formulaire_client'))

        cur.execute("SELECT id FROM client WHERE email = %s", (email,))
        if cur.fetchone():
            flash("❌ Cet email est déjà utilisé.", "danger")
            return redirect(url_for('afficher_formulaire_client'))

        # Tout est bon : insérer
        cur.execute("""
            INSERT INTO client (nom_societe, ice, adresse, telephone, email, periode_echeance)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nom_societe, ice, adresse, telephone, email, periode_echeance))

        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Client ajouté avec succès.", "success")
    except Exception as e:
        print("Erreur SQL :", e)
        flash(f"❌ Erreur lors de l'ajout du client : {str(e)}", "error")

    return redirect(url_for('afficher_formulaire_client'))
 

# ============ ROUTES FACTURES =============
@app.route('/ajouter-facture', methods=['GET'])
@login_required
def afficher_formulaire_facture():
    conn = get_db_connection()
    cur = conn.cursor()

    # Récupérer la liste des clients
    cur.execute("SELECT id, nom_societe, periode_echeance FROM client")
    clients = cur.fetchall()

    # Récupérer le dernier numéro de facture
    cur.execute("SELECT numero FROM facture ORDER BY id DESC LIMIT 1")
    last = cur.fetchone()
    dernier_numero = last[0] if last else ""

    cur.close()
    conn.close()

    return render_template('ajouter_facture.html', clients=clients, dernier_numero=dernier_numero)



@app.route('/ajouter-facture', methods=['POST'])
@login_required
def ajouter_facture():
    try:
        numero = request.form['numero']
        date_facture = datetime.strptime(request.form['date_facture'], '%Y-%m-%d')
        camion = request.form['matricule']
        remorque = request.form['remorque']
        description = request.form['description']
        ligne_depart = request.form['ligne_depart']
        ligne_destination = request.form['ligne_arrivee']
        montant_ht = float(request.form['montant'])
        tva = float(request.form['tva'])
        devise = request.form['devise']
        date_echeance = request.form.get('date_echeance', (date_facture + timedelta(days=30)).strftime('%Y-%m-%d'))
        statut= request.form.get('statut', 'impayée')  # Valeur par défaut
        client_id = int(request.form['client_id'])
        
        montant_ttc = round(montant_ht * (1 + tva / 100), 2)
        montant_lettres = convertir_en_lettres(montant_ttc, devise)

        conn = get_db_connection()
        cur = conn.cursor()
         # Obtenir la période d'échéance du client
        cur.execute("SELECT periode_echeance FROM client WHERE id = %s", (client_id,))
        result = cur.fetchone()
        periode = result[0] if result else 30
        date_echeance = date_facture + timedelta(days=periode)

        cur.execute("""
            INSERT INTO facture (numero, date_facture, camion, remorque, description,
                                 montant, montant_lettres, tva, montant_ttc, devise,
                                 client_id, ligne_depart, ligne_destination, statut, date_echeance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            numero, date_facture, camion, remorque, description,
            montant_ht, montant_lettres, tva, montant_ttc, devise,
            client_id, ligne_depart, ligne_destination, statut, date_echeance
        ))
        conn.commit()
        cur.close()
        conn.close()

        flash(f"✅ Facture {numero} enregistrée avec succès.", "success")
    except Exception as e:
        flash(f"❌ Erreur lors de l'enregistrement : {str(e)}", "error")

    return redirect(url_for('afficher_formulaire_facture'))



# ============ ROUTE AFFICHAGE FACTURES JSON (API) =============
@app.route('/api/factures', methods=['GET'])
@login_required
def get_factures():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.numero, f.date_facture, c.nom_societe, f.camion, f.remorque, c.periode_echeance,
               f.ligne_depart, f.ligne_destination, f.montant, f.tva, f.montant_ttc, f.devise,f.statut, f.date_echeance
        FROM facture f
        JOIN client c ON f.client_id = c.id
        ORDER BY f.numero DESC
    """)
    factures = cur.fetchall()
    cur.close()
    conn.close()

    factures_liste = [
        {
            'numero': f[0],
            'date': f[1].strftime('%Y-%m-%d'),
            'nom_societe': f[2],
            'camion': f[3],
            'remorque': f[4],
            'periode_echeance': f[5],
            'ligne_depart': f[6],
            'ligne_destination': f[7],
            'montant': f[8],
            'tva': f[9],
            'montant_ttc': f[10],
            'devise': f[11],
            'statut': f[12],
            'date_echeance': f[13]
        } for f in factures
    ]

    return {'factures': factures_liste}





# ============ ROUTE LISTE FACTURES (HTML) =============
@app.route('/liste-factures')
@login_required
def liste_factures():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.id, f.numero, f.date_facture, c.nom_societe,f.camion, f.remorque, c.periode_echeance,f.ligne_depart, f.ligne_destination ,f.montant,f.tva,f.montant_ttc, f.devise,f.date_echeance,f.statut
        FROM facture f
        JOIN client c ON f.client_id = c.id
        ORDER BY f.numero DESC
    """)
    factures = cur.fetchall()
    cur.close()
    conn.close()
    # Convertir les champs date (date_facture = index 2, date_echeance = index 13) si ce sont des chaînes
    factures_formatees = []
    for f in factures:
        f_list = list(f)

        if isinstance(f_list[2], str):
            try:
                f_list[2] = datetime.strptime(f_list[2], '%Y-%m-%d')
            except ValueError:
                pass

        if isinstance(f_list[13], str):
            try:
                f_list[13] = datetime.strptime(f_list[13], '%Y-%m-%d')
            except ValueError:
                pass

        factures_formatees.append(f_list)

    return render_template('liste_factures.html', factures=factures_formatees,datetime=datetime, timedelta=timedelta)


    return render_template('liste_factures.html', factures=factures)


# ============ ROUTE GENERATION PDF FACTURE =============
@app.route('/facture/<int:facture_id>/pdf')
@login_required
def telecharger_facture(facture_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.numero, f.date_facture, f.camion, f.remorque, f.description,
               f.ligne_depart, f.ligne_destination, f.montant, f.montant_lettres,
               f.tva, f.montant_ttc, f.devise,
               c.nom_societe, c.ice, c.adresse, c.telephone, c.email
        FROM facture f
        JOIN client c ON f.client_id = c.id
        WHERE f.id = %s
    """, (facture_id,))
    facture = cur.fetchone()
    cur.close()
    conn.close()

    if not facture:
        flash("❌ Facture introuvable", "error")
        return redirect(url_for('liste_factures'))

    # Préparer les données pour le template
    data = {
        'numero': facture[0],
        'date_facture': facture[1].strftime('%d/%m/%Y'),
        'camion': facture[2],
        'remorque': facture[3],
        'description': facture[4],
        'ligne_depart': facture[5],
        'ligne_destination': facture[6],
        'montant': facture[7],
        'montant_lettres': facture[8],
        'tva': facture[9],
        'montant_ttc': facture[10],
        'devise': facture[11],
        'nom_societe': facture[12],
        'ice': facture[13],
        'adresse': facture[14],
        'telephone': facture[15],
        'email': facture[16],
        'logo_path': url_for('static', filename='logo.png', _external=True),

        'css_path': url_for('static', filename='style.css'),
    }

    html = render_template('formFacture.html', facture=data)
    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file, stylesheets=[CSS(url_for('static', filename='style.css', _external=True))])
    pdf_file.seek(0)

    return send_file(pdf_file, download_name=f"facture_{data['numero']}.pdf", as_attachment=True)


# ============ ROUTES MODIFIER FACTURE =============
@app.route('/facture/<int:facture_id>/modifier', methods=['GET'])
@login_required
def modifier_facture(facture_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nom_societe FROM client")
    clients = cur.fetchall()

    cur.execute("""
        SELECT id, numero, date_facture, camion, remorque, description, 
               montant, tva, devise, client_id, ligne_depart, ligne_destination, statut
        FROM facture WHERE id = %s
    """, (facture_id,))
    facture = cur.fetchone()

    cur.close()
    conn.close()

    if not facture:
        flash("❌ Facture introuvable", "error")
        return redirect(url_for('liste_factures'))

    return render_template('modifier_facture.html', facture=facture, clients=clients)


@app.route('/facture/<int:facture_id>/modifier', methods=['POST'])
@login_required
def enregistrer_modification_facture(facture_id):
    try:
        numero = request.form['numero']
        date_facture = request.form['date_facture']
        camion = request.form['matricule']
        remorque = request.form['remorque']
        description = request.form['description']
        ligne_depart = request.form['ligne_depart']
        ligne_destination = request.form['ligne_arrivee']
        montant_ht = float(request.form['montant'])
        tva = float(request.form['tva'])
        devise = request.form['devise']
        statut = request.form.get('statut', 'impayée')  # Valeur par défaut
        client_id = int(request.form['client_id'])

        montant_ttc = round(montant_ht * (1 + tva / 100), 2)
        montant_lettres = convertir_en_lettres(montant_ttc, devise)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE facture
            SET numero = %s, date_facture = %s, camion = %s, remorque = %s,
                description = %s, montant = %s, montant_lettres = %s,
                tva = %s, montant_ttc = %s, devise = %s,
                client_id = %s, ligne_depart = %s, ligne_destination = %s,statut = %s
            WHERE id = %s
        """, (
            numero, date_facture, camion, remorque, description,
            montant_ht, montant_lettres, tva, montant_ttc, devise,
            client_id, ligne_depart, ligne_destination, statut, facture_id
        ))
        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Facture modifiée avec succès.", "success")
        return redirect(url_for('liste_factures'))
    except Exception as e:
        flash(f"❌ Erreur lors de la modification : {str(e)}", "error")
        return redirect(url_for('modifier_facture', facture_id=facture_id))


# ============ ROUTE SUPPRIMER FACTURE =============
@app.route('/facture/<int:facture_id>/supprimer', methods=['POST'])
@login_required
def supprimer_facture(facture_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM facture WHERE id = %s", (facture_id,))
        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Facture supprimée.", "success")
    except Exception as e:
        flash(f"❌ Erreur lors de la suppression : {str(e)}", "error")

    return redirect(url_for('liste_factures'))

# ============ ROUTE RECHERCHE FACTURE =============
@app.route('/factures', methods=['GET'])
@login_required
def affichage_facture():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Récupération des filtres
    search = request.args.get('search', '').strip()
    date_min = request.args.get('date_min')
    date_max = request.args.get('date_max')
    echeance_min = request.args.get('echeance_min')
    echeance_max = request.args.get('echeance_max')
    montant_min = request.args.get('montant_min')
    montant_max = request.args.get('montant_max')
    ligne_depart = request.args.get('ligne_depart')
    ligne_arrivee = request.args.get('ligne_arrivee')
    devise = request.args.get('devise')

    query = """
        SELECT f.id, f.numero, f.date_facture, c.nom_societe, f.camion, f.remorque,
               f.description, f.ligne_depart, f.ligne_destination, f.montant,
               f.tva, f.montant_ttc, f.devise, f.date_echeance, f.statut
        FROM facture f
        JOIN client c ON f.client_id = c.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (f.numero LIKE %s OR c.nom_societe LIKE %s OR f.statut = %s)"
        search_param = f"%{search}%"
        params += [search_param, search_param, search]

    if date_min:
        query += " AND f.date_facture >= %s"
        params.append(date_min)
    if date_max:
        query += " AND f.date_facture <= %s"
        params.append(date_max)

    if echeance_min:
        query += " AND f.date_echeance >= %s"
        params.append(echeance_min)
    if echeance_max:
        query += " AND f.date_echeance <= %s"
        params.append(echeance_max)

    if montant_min:
        query += " AND f.montant_ttc >= %s"
        params.append(montant_min)
    if montant_max:
        query += " AND f.montant_ttc <= %s"
        params.append(montant_max)

    if ligne_depart:
        query += " AND f.ligne_depart LIKE %s"
        params.append(f"%{ligne_depart}%")

    if ligne_arrivee:
        query += " AND f.ligne_destination LIKE %s"
        params.append(f"%{ligne_arrivee}%")

    if devise:
        query += " AND f.devise = %s"
        params.append(devise)

    query += " ORDER BY f.numero DESC"
    cursor.execute(query, params)
    factures = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("liste_factures.html", factures=factures, search=search, datetime=datetime, timedelta=timedelta,
        date_min=date_min, date_max=date_max, echeance_min=echeance_min, echeance_max=echeance_max,
        montant_min=montant_min, montant_max=montant_max, 
        ligne_depart=ligne_depart, ligne_arrivee=ligne_arrivee, devise=devise)


# ============ ROUTE LISTE CLIENT (HTML) =============
@app.route('/liste-clients')
@login_required
def liste_clients():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.nom_societe, c.ice, c.adresse, c.telephone, c.email, c.periode_echeance
        FROM client c
        ORDER BY c.nom_societe ASC
    """)
    clients = cur.fetchall()
    cur.close()
    conn.close()
    

    return render_template('liste_clients.html', clients=clients)
# ============ ROUTES MODIFIER CLIENT =============
@app.route('/clients/<int:client_id>/modifier', methods=['GET'])
@login_required
def modifier_client(client_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nom_societe, ice, adresse, telephone, email, periode_echeance FROM client WHERE id = %s", (client_id,))
    client = cur.fetchone()

    cur.close()
    conn.close()

    if not client:
        flash("❌ Client introuvable", "error")
        return redirect(url_for('liste_clients'))

    return render_template('modifier_client.html', client=client)

   


@app.route('/clients/<int:client_id>/modifier', methods=['POST'])
@login_required
def enregistrer_modification_client(client_id):
    try:
        nom_societe = request.form['nom_societe']
        ice = request.form['ice']
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        email = request.form['email']
        periode_echeance = int(request.form.get('periode_echeance'or 30))  # Valeur par défaut de 30 jours

        conn = get_db_connection()
        cur = conn.cursor()
       # Mise à jour du client
        cur.execute("""
    UPDATE client
    SET nom_societe = %s, ice = %s, adresse = %s, telephone = %s, email = %s, periode_echeance = %s
    WHERE id = %s
""", (nom_societe, ice, adresse, telephone, email, periode_echeance, client_id))

# Mise à jour des dates d’échéance des factures impayées
        cur.execute("""
    UPDATE facture
    SET date_echeance = DATE_ADD(date_facture, INTERVAL %s DAY)
    WHERE client_id = %s AND statut != 'payée'
""", (periode_echeance, client_id))


        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Client modifié avec succès.", "success")
        return redirect(url_for('liste_clients'))
    except Exception as e:
        flash(f"❌ Erreur lors de la modification : {str(e)}", "error")
        return redirect(url_for('modifier_client', client_id=client_id))


   

# ============ ROUTE SUPPRIMER CLIENT=============
@app.route('/clients/<int:client_id>/supprimer', methods=['POST'])
@login_required
def supprimer_client(client_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Vérifier que le client existe
        cur.execute("SELECT id FROM client WHERE id = %s", (client_id,))
        if not cur.fetchone():
            flash("❌ Client introuvable.", "error")
            cur.close()
            conn.close()
            return redirect(url_for('liste_clients'))

        # Suppression
        cur.execute("DELETE FROM client WHERE id = %s", (client_id,))
        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Client supprimé.", "success")
    except Exception as e:
        flash(f"❌ Erreur lors de la suppression : {str(e)}", "error")

    return redirect(url_for('liste_clients'))


# ============ ROUTE RECHERCHE CLIENT =============
@app.route('/clients', methods=['GET'])
@login_required
def affichage_clients():
    conn = get_db_connection()
    cursor = conn.cursor()  # Ouvre le curseur après avoir obtenu la connexion

    search = request.args.get('search')
    params = ()
    query = """
        SELECT c.id, c.nom_societe, c.ice, c.adresse, c.telephone, c.email, c.periode_echeance
        FROM client c
    """

    if search:
        query += " WHERE c.ice LIKE %s OR c.nom_societe LIKE %s OR c.email LIKE %s"
        search_param = f"%{search}%"
        params = (search_param, search_param, search_param)

    query += " ORDER BY c.nom_societe DESC"
    cursor.execute(query, params)  # ⚠️ C’est ici que l’erreur se produit si le curseur est fermé
    clients = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("liste_clients.html", clients=clients, search=search or "")

# ============ ROUTE CHANGER STATUT FACTURE =============
@app.route('/changer-statut/<int:facture_id>', methods=['POST'])
@login_required
def changer_statut(facture_id):
    data = request.get_json()
    nouveau_statut = data.get('nouveau_statut')

    if nouveau_statut not in ['payée', 'impayée']:
        return jsonify({'success': False, 'message': 'Statut invalide'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE facture SET statut = %s WHERE id = %s", (nouveau_statut, facture_id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    

    # ============ ROUTES AUTHENTIFICATION ============="
    # 🔐 Page de connexion
@app.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        login_input = request.form['login']
        mot_de_passe_input = request.form['mot_de_passe']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM utilisateur WHERE login = %s', (login_input,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['mot_de_passe'], mot_de_passe_input):
            session['user_id'] = user['id']
            session['user_login'] = user['login']
            flash('Connexion réussie', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login ou mot de passe incorrect', 'danger')

    return render_template('login.html')

# 🔐 Déconnexion
@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnexion réussie', 'info')
    return redirect(url_for('login'))

# 🔐 Page d'accueil
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

if __name__ == '__main__':
    # En debug uniquement en développement
    app.run(debug=True)
