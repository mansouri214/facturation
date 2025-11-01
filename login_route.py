from flask import Flask, render_template, request, redirect, url_for, session, flash
from db import get_db_connection
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'remplace_ça_par_une_clé_ultra_secrète'  # Change ceci en prod !
bcrypt = Bcrypt(app)

# 🔐 Crée un compte admin par défaut si inexistant
def creer_compte_admin_defaut():
    login_defaut = "admin"
    mot_de_passe_defaut = "admin123"
    email_defaut = "admin@admin.com"

    hashed = bcrypt.generate_password_hash(mot_de_passe_defaut).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Vérifie si un compte admin existe déjà
    cursor.execute("SELECT id FROM utilisateur WHERE login = %s", (login_defaut,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute(
            "INSERT INTO utilisateur (login, mot_de_passe, email) VALUES (%s, %s, %s)",
            (login_defaut, hashed, email_defaut)
        )
        conn.commit()
        print("✅ Compte admin par défaut créé.")
    else:
        print("ℹ️ Le compte admin existe déjà.")

    cursor.close()
    conn.close()

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


# 🔁 Lancement de l'app
if __name__ == '__main__':
    creer_compte_admin_defaut()
    app.run(debug=True)
