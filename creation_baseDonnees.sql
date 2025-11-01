CREATE DATABASE facturation;

CREATE TABLE client (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_societe VARCHAR(255) DEFAULT NULL,
    ice VARCHAR(50) DEFAULT NULL,
    adresse TEXT DEFAULT NULL,
    complement_adresse TEXT DEFAULT NULL,
    telephone VARCHAR(20) DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL
);
CREATE TABLE facture (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(50) NOT NULL UNIQUE,
    date_facture DATE NOT NULL,
    camion VARCHAR(100) DEFAULT NULL,
    remorque VARCHAR(100) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    trajet VARCHAR(255) DEFAULT NULL,
    montant FLOAT DEFAULT NULL,
    montant_lettres VARCHAR(255) DEFAULT NULL,
    tva FLOAT DEFAULT 0,
    montant_ttc FLOAT DEFAULT NULL,
    devise VARCHAR(10) DEFAULT 'MAD',
    client_id INT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES client(id) ON DELETE CASCADE
);
