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

---

## 🏗️ Architecture Globale

```text
  [ Source de Données / API ]
               │
               ▼
   ┌───────────────────────┐
   │  GridConnect Client   │  <-- Extrait les métriques brutes
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │   Measure (Modèle)    │  <-- Conversion en objets métier typés
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │  MeasureValidator     │  <-- Détection des anomalies / valeurs aberrantes
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │ PostgreSQL Repository │  <-- Stockage prospectif & idempotent
   └───────────────────────┘
               │
               ▼
   ┌───────────────────────┐
   │  Grafana Dashboards   │  <-- Visualisation & analyses énergétiques
   └───────────────────────┘
```

---

## 🚀 Fonctionnalités principales

- **Parsing multi-sources :** Support des exports CSV historiques et des appels d'API HTTP internes.
- **Modèle de données typé :** Immutabilité des mesures et calcul automatique de la puissance équivalente (kW sur 15 min).
- **Détection des anomalies :** Isolation des pointes physiquement irréalistes ou des erreurs d'acquisition pour éviter de fausser les analyses statistiques et tarifaires.
- **Schéma PostgreSQL prêt à l'emploi :** Indexation sur `(timestamp, ean, register)` et contrainte d'unicité pour les rechargements idempotents.

---

## 🛠️ Installation & Préréquis

### Prérequis

- Python 3.10+
- PostgreSQL 13+
- Grafana (optionnel, pour la visualisation)

### Installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/GridConnect.git
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
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuration

Copier le fichier d'exemple et configurer vos paramètres locaux :

```bash
cp .env.example .env
```

Le fichier `.env` permet de définir :
- Les identifiants de connexion PostgreSQL.
- Les identifiants de points de fourniture (EAN) anonymisés / configurés localement.
- Les jetons / cookies de session requis pour les requêtes HTTP locales.

> ⚠️ **Sécurité :** Ne commitez **jamais** votre fichier `.env` ni aucun fichier contenant vos vraies données personnelles ou identifiants de session sur GitHub.

---

## 📂 Structure du Projet

```text
GridConnect/
├── .env.example              # Modèle de configuration locale
├── .gitignore                # Exclusion des secrets et de l'environnement virtuel
├── README.md                 # Documentation du projet
├── requirements.txt          # Dépendances Python
├── config/                   # Fichiers de configuration
├── scripts/                  # Scripts d'exécution et d'import
└── src/
    └── gridconnect/          # Package Python principal
        ├── __init__.py
        ├── client.py         # Client d'extraction API / Réseau
        ├── models.py         # Modèle métier (Measure, RegisterType)
        ├── parsers.py        # Connecteurs de lecture (CSV, JSON)
        ├── repository.py     # Couche d'accès aux données PostgreSQL
        └── validation.py     # Moteur de contrôle et d'anomalies
```

---

## 📜 Licence

Ce projet est sous licence MIT. Libre à vous de le réutiliser, de l'adapter et de contribuer !