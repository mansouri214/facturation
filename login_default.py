from werkzeug.security import generate_password_hash
from db import get_db_connection
def creer_compte_par_defaut():
    conn = get_db_connection()
    cur = conn.cursor()
    login_defaut = "admin"
    email_defaut = "admin@example.com"
    motdepasse_defaut = "admin123"  # à changer !
    

    # Vérifier si le compte existe déjà
    cur.execute("SELECT id FROM utilisateur WHERE login = %s", (login_defaut,))
    user = cur.fetchone()

    if not user:
        # Hashage du mot de passe
        motdepasse_hash = generate_password_hash(motdepasse_defaut)

        # Insérer le compte admin par défaut
        cur.execute("""
            INSERT INTO utilisateur (login, email, password)
            VALUES (%s, %s, %s, %s)
        """, (login_defaut, email_defaut, motdepasse_hash))
        conn.commit()
        print("Compte admin par défaut créé.")
    else:
        print("Compte admin par défaut déjà existant.")

    cur.close()
    conn.close()
