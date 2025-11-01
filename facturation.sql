-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : lun. 07 juil. 2025 à 22:12
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `facturation`
--

-- --------------------------------------------------------

--
-- Structure de la table `client`
--

CREATE TABLE `client` (
  `id` int(11) NOT NULL,
  `nom_societe` varchar(255) DEFAULT NULL,
  `ice` varchar(50) DEFAULT NULL,
  `adresse` text DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `type` varchar(100) DEFAULT NULL,
  `periode_echeance` int(11) NOT NULL DEFAULT 30
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `client`
--

INSERT INTO `client` (`id`, `nom_societe`, `ice`, `adresse`, `telephone`, `email`, `type`, `periode_echeance`) VALUES
(1, 'Transport SA', '1234567890001', 'Rue des transport', '212060500000', 'contactus@transport.ma', NULL, 90),
(3, 'Transport SONAF', '009974563210', 'Rue Belgrade RABAT', '212670859869', 'sonaf@logistique.com', NULL, 30),
(4, 'Transport Marhaba', '001234567890', 'Rue AUSTRALIE RABAT', '212660096577', 'marhaba@gmail.com', NULL, 30),
(5, 'ICE Maghreb', '000203949000067', 'Complexe Dali, zone industrielle Lissasfa, Casablanca', '212522201422', 'contact@icemaghreb.com', NULL, 120),
(9, 'Maroc Équipement Service', '000090309000043', '108 Rue d’Ifni, La Gironde, Casablanca', '212522450315', 'equipementmaroc@gmail.com', NULL, 30),
(10, 'TechNova Solutions SARL', '00214578900013', '15 Rue Ibnou Sina, Casablanca, Maroc', '212522456789', 'contact@technova.ma', NULL, 90);

-- --------------------------------------------------------

--
-- Structure de la table `facture`
--

CREATE TABLE `facture` (
  `id` int(11) NOT NULL,
  `numero` varchar(50) NOT NULL,
  `date_facture` date NOT NULL,
  `camion` varchar(100) DEFAULT NULL,
  `remorque` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `ligne_depart` varchar(100) DEFAULT NULL,
  `ligne_destination` varchar(100) DEFAULT NULL,
  `montant` float DEFAULT NULL,
  `montant_lettres` varchar(255) DEFAULT NULL,
  `tva` float DEFAULT 0,
  `montant_ttc` float DEFAULT NULL,
  `devise` varchar(10) DEFAULT 'MAD',
  `statut` enum('payée','impayée') DEFAULT 'impayée',
  `client_id` int(11) NOT NULL,
  `date_echeance` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `facture`
--

INSERT INTO `facture` (`id`, `numero`, `date_facture`, `camion`, `remorque`, `description`, `ligne_depart`, `ligne_destination`, `montant`, `montant_lettres`, `tva`, `montant_ttc`, `devise`, `statut`, `client_id`, `date_echeance`) VALUES
(1, '1/25', '2025-06-12', ' 88364-B-55', 'R-8766-ZDS', 'TRANSPORT INTERNATIONNAL', 'EL JADIDA', 'PARIS', 3000, 'TROIS MILLE QUATRE CENT CINQUANTE EUROS', 15, 3450, 'EUR', 'impayée', 1, '2025-09-10'),
(2, '2/25', '2025-06-28', ' 88364-B-44', 'R-8766-ZVB', 'TRANSPORT INTERNATIONNAL', 'FES', 'JEDDA', 3333, 'TROIS MILLE NEUF CENT QUATRE-VINGT-DIX-NEUF DOLLARS ET SOIXANTE CENTIMES', 20, 3999.6, 'USD', 'payée', 3, '2025-08-27'),
(3, '3/25', '2025-06-14', ' 88364-B-1', 'R-8766-ZDS', 'TRANSPORT INTERNATIONNAL', 'RABAT', 'MADRID', 6000, 'SEPT MILLE CINQ CENTS EUROS', 25, 7500, 'EUR', 'payée', 5, '2025-10-12'),
(4, '4/25', '2025-06-16', ' 88364-B-55', 'R-8766-ZDS', 'TRANSPORT INTERNATIONNAL', 'RABAT', 'PARIS', 3500, 'QUATRE MILLE TROIS CENT SOIXANTE-QUINZE DOLLARS', 25, 4375, 'USD', 'payée', 5, '2025-10-14'),
(7, '5/25', '2025-05-19', ' 88364-B-55', 'R-8766-ZDS', 'Transport internationnal', 'MARRAKECH', 'MADRID', 3256, 'TROIS MILLE SEPT CENT QUARANTE-QUATRE EUROS ET QUARANTE CENTIMES', 15, 3744.4, 'EUR', 'impayée', 9, '2025-06-18'),
(11, '6/25', '2025-05-24', ' 88364-B-44', 'R-8766-DBV', 'TRANSPORT INTERNATIONNAL', 'RABAT', 'TOULOUSE', 7500, 'NEUF MILLE EUROS', 20, 9000, 'EUR', 'impayée', 3, '2025-06-23'),
(12, '7/25', '2025-05-23', ' 88364-B-44', 'R-8766-DBV', 'TRANSPORT', 'TANGIER', 'TOULOUSE', 8500, 'DIX MILLE DEUX CENTS EUROS', 20, 10200, 'EUR', 'impayée', 4, '2025-06-22');

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

CREATE TABLE `utilisateur` (
  `id` int(11) NOT NULL,
  `login` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `utilisateur`
--

INSERT INTO `utilisateur` (`id`, `login`, `email`, `mot_de_passe`) VALUES
(3, 'admin', 'admin@admin.com', '$2b$12$9b1fJPBJrUsiF9S/2C2gvuwsiGlcQqcXYrIVkfeqwc.A2vIpKse.m');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `client`
--
ALTER TABLE `client`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ice` (`ice`),
  ADD UNIQUE KEY `telephone` (`telephone`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `unique_nom_societe` (`nom_societe`),
  ADD UNIQUE KEY `unique_ice` (`ice`),
  ADD UNIQUE KEY `unique_telephone` (`telephone`),
  ADD UNIQUE KEY `unique_email` (`email`);

--
-- Index pour la table `facture`
--
ALTER TABLE `facture`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero` (`numero`),
  ADD UNIQUE KEY `date_facture` (`date_facture`),
  ADD KEY `client_id` (`client_id`);

--
-- Index pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `login` (`login`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `client`
--
ALTER TABLE `client`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT pour la table `facture`
--
ALTER TABLE `facture`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT pour la table `utilisateur`
--
ALTER TABLE `utilisateur`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `facture`
--
ALTER TABLE `facture`
  ADD CONSTRAINT `facture_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
