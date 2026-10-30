# GridConnect

**GridConnect** est un connecteur Python open source conçu pour récupérer, valider et stocker localement les données de consommation et de production électriques issues de compteurs communicants (notamment via les portails de gestionnaires de réseau comme ORES en Belgique).

Le projet transforme les séries temporelles brutes en objets métier Python typés, assure un contrôle de validité des données, puis les persiste dans une base de données PostgreSQL pour exploitation analytique sous Grafana.

---

## 🎯 Objectifs du projet

- **Autonomie & Réappropriation des données :** Permettre aux particuliers de conserver un historique local complet et indépendant de leurs relevés quart-horaires.
- **Architecture Orientée Objet (POO) :** Modélisation propre et robuste autour d'objets métier (`Measure`).
- **Idempotence & Intégrité :** Ingestion sans doublons, conservation de l'historique brut et marquage explicite des valeurs aberrantes sans altération des données sources.
- **Compatibilité Grafana :** Schéma PostgreSQL optimisé pour la visualisation des séries temporelles (consommation, production, puissance calculée).
- **Conception Générique :** Architecture modulaire réutilisable pour différents points de fourniture (EAN) et plusieurs registres (heures pleines / heures creuses, injection / prélèvement).
- **Déploiement conteneurisé & résilient :** Exécution continue en arrière-plan via un démon Docker permanent sur serveur Linux, garantissant une collecte automatisée et autonome.

---

## 🏗️ Architecture Globale

```text
  [ Source de Données / API ]
               │
               ▼
   ┌───────────────────────┐
   │     OresApiClient     │  <-- Extrait les métriques brutes
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │        Measure        │  <-- Conversion en objets métier typés et détection des anomalies / valeurs aberrantes
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │        DBStore        │  <-- Stockage prospectif & idempotent
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │  Grafana Dashboards   │  <-- Visualisation & analyses énergétiques
   └───────────────────────┘
```

---

## 🚀 Fonctionnalités principales
- **Modèle de données typé :** Immutabilité des mesures et calcul automatique de la puissance équivalente (kW sur 15 min).
- **Détection des anomalies :** Isolation des pointes physiquement irréalistes ou des erreurs d'acquisition pour éviter de fausser les analyses statistiques et tarifaires.
- **Schéma PostgreSQL prêt à l'emploi :** Indexation sur `(read_at, register)` et contrainte d'unicité pour les rechargements idempotents.
- **Authentification & Déploiement distant :** Capture de la session myORES via Playwright et transfert automatique optionnel du jeton (session.json) vers un serveur distant via SCP.
- **Démon de surveillance asynchrone :** Service Docker léger qui surveille l'actualisation du jeton de session pour lancer la collecte à la demande sans solliciter inutilement l'API.

---

## 🛠️ Installation & Préréquis

### Prérequis

- Python 3.10+
- PostgreSQL 13+ & TimescaleDB
- Grafana (optionnel, pour la visualisation)

### Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/ArnaudClarat/GridConnect.git
   cd GridConnect
   ```

2. Créer et activer un environnement virtuel :
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Sur Linux/macOS
   # ou: .venv\Scripts\activate  # Sur Windows
   ```

3. Installer les dépendances :
   ```bash
      pip install -r requirements.txt          # suffisant pour collector.py
   pip install -r requirements-login.txt    # à ajouter pour login.py
   playwright install chromium              # à ajouter pour login.py
   ```

---

## ⚙️ Utilisation & Déploiement

- **`scripts/login.py` :** Ouvre le navigateur sur ton PC local, gère l'authentification itsme et enregistre le jeton dans `config/session.json`.
- **`scripts/collector.py` :** Script unitaire de récupération des mesures et d'enregistrement en base.
- **`scripts/daemon.py` :** Démon permanent exécuté dans un conteneur Docker sur le serveur, qui surveille en continu la modification du fichier de session pour déclencher la collecte automatiquement.


## ⚙️ Configuration

Copier le fichier d'exemple et configurer vos paramètres locaux :

```bash
cp .env.example .env
```

Le fichier `.env` permet de définir :
- Les identifiants de connexion PostgreSQL.
- Les identifiants de points de fourniture (EAN) anonymisés / configurés localement.
- Les paramètres de déploiement SSH/SCP vers un serveur distant (REMOTE_SERVER_*) pour le transfert automatique de la session session.json.
- `DAEMON_CHECK_INTERVAL` : L'intervalle de temps (en secondes) séparant chaque vérification du fichier de session par le démon (ex: `3660`).

> ⚠️ **Sécurité :** Ne commitez **jamais** votre fichier `.env` ni aucun fichier contenant vos vraies données personnelles ou identifiants de session sur GitHub.

---

## 🐳 Conteneurisation (Docker)

Le projet intègre un `Dockerfile` optimisé (basé sur Python 3.13 slim) ainsi qu'un `.dockerignore` configuré pour exclure les fichiers locaux et runtimes superflus du contexte de build.

Pour lancer le service de collecte en arrière-plan sur ton serveur :

```bash
# 1. Construire l'image
docker build -t gridconnect-collector .

# 2. Lancer le conteneur persistant
docker run -d \
  --name gridconnect-collector \
  --restart unless-stopped \
  --env-file .env \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  gridconnect-collector
```

---

## 📂 Structure du Projet

```text
GridConnect/
├── .dockerignore              # Exclusion des fichiers locaux et runtimes du contexte Docker
├── .env.example               # Modèle de configuration locale
├── .gitignore                 # Exclusion des secrets et des artefacts Python
├── Dockerfile                 # Configuration de l'image de conteneurisation du démon
├── pyproject.toml             # Configuration du paquet Python (pip install -e .)
├── README.md                  # Documentation du projet
├── requirements.txt           # Dépendances Python
├── requirements-login.txt     # Dépendances supplémentaires pour login.py
├── config/                    # Fichiers de configuration et de session (session.json)
├── scripts/                   # Scripts d'exécution
│   ├── login.py               # Capture interactive et déploiement SSH de la session
│   ├── collector.py           # Test d'extraction et de collecte headless
│   └── daemon.py              # Démon de surveillance permanent (Docker)
└── src/
    └── gridconnect/           # Package Python principal
        ├── __init__.py
        ├── client.py          # Client d'extraction API / Réseau
        ├── db.py              # Enregistrement dans TimescaleDB
        ├── models.py          # Modèle métier (Measure, RegisterType)
        └── auth/              # Module d'authentification et gestion de session
            ├── __init__.py
            └── session.py     # Modèle OresSession et SessionManager
```

---

## 📜 Licence

Ce projet est sous licence **CC BY‑NC 4.0** (Attribution – NonCommercial).

Vous pouvez utiliser, copier, modifier et partager ce projet librement pour un usage personnel ou non commercial.  
Toute utilisation commerciale, y compris l’intégration dans un produit ou service payant, est interdite sans mon accord explicite.
