# 🩸 BloodConnect - Plateforme de Don de Sang

**BloodConnect** est une plateforme web développée avec Django permettant de mettre en relation des donneurs volontaires et des établissements hospitaliers. Ce projet a été réalisé dans le cadre de l'évaluation du module "Développement Web avec Django" (Année 2025-2026).

## 🚀 Fonctionnalités principales

### 👨‍💼 Administration
- **Tableau de Bord National** : Statistiques en temps réel (donneurs, hôpitaux, dons).
- **Validation des Hôpitaux** : Vérification des licences médicales (PDF) avant activation.
- **Carte des Urgences** : Visualisation géographique des besoins par ville (Leaflet.js).
- **Export de données** : Export CSV de la liste des donneurs.

### 🏥 Espace Hôpital
- **Gestion des Demandes** : Publication et clôture de demandes urgentes de sang.
- **Campagnes de Collecte** : Organisation de collectes avec gestion des créneaux horaires.
- **Gestion du Stock** : Suivi des poches de sang disponibles et alertes de pénurie.
- **Consultation des Réponses** : Visualisation des donneurs ayant répondu aux appels.

### 👤 Espace Donneur
- **Calcul d'Éligibilité** : Calcul automatique de la prochaine date de don (56 jours H / 84 jours F).
- **Appels Compatibles** : Filtrage intelligent des demandes selon le groupe sanguin.
- **Historique des Dons** : Suivi complet des dons effectués.
- **Inscription aux Campagnes** : Choix de créneaux avec gestion de capacité.

## 🛠️ Installation locale

1. **Cloner le projet**
   ```bash
   git clone https://github.com/Mariem938/projet-don-de-sang.git
   cd projet-don-de-sang
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Migrations et lancement**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 📋 Données de test
- **Admin** : adminDon / Admin@2026
- **Hôpitaux** : au moins 2 comptes validés inclus.
- **Donneurs** : au moins 5 profils avec groupes sanguins variés.

## ⚖️ Règles métier implémentées
- Respect strict de la matrice de compatibilité sanguine.
- Délai entre deux dons contrôlé à l'inscription.
- Seuls les hôpitaux validés par l'admin peuvent publier des appels.
- Capacité maximale par créneau de campagne.

---
**BloodConnect** — *Donner son sang, c'est sauver des vies.* 🔴
