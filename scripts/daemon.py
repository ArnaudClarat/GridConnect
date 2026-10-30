import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Ajout du dossier 'src' au path Python pour permettre les imports du package gridconnect
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

# Chargement des variables d'environnement
load_dotenv()

# Import de la fonction principale de collecte
from collector import main as collect

# Chemin vers le fichier de session généré par login.py
SESSION_FILE = Path("/app/config/session.json")

# Intervalle de vérification (par défaut: 60 secondes)
try:
    CHECK_INTERVAL = int(os.getenv("DAEMON_CHECK_INTERVAL", 60))
except ValueError:
    print("Valeur invalide pour DAEMON_CHECK_INTERVAL. Utilisation de la valeur par défaut : 60s.", flush=True)
    CHECK_INTERVAL = 60


def run_collection_pipeline() -> None:
    """Exécute le pipeline de collecte de données et gère les erreurs."""
    print("Mise à jour du fichier de session détectée. Lancement de la collecte ORES...", flush=True)
    try:
        collect()
        print("Collecte des données terminée avec succès.", flush=True)
    except Exception as e:
        print(f"Erreur lors de la collecte des données : {e}", flush=True)


def watch_session() -> None:
    """
    Surveille la date de dernière modification du fichier de session
    et trace chaque cycle de vie dans les logs.
    """
    print("Démarrage du démon GridConnect...", flush=True)
    print(f"Fichier surveillé : {SESSION_FILE}", flush=True)
    print(f"Intervalle de vérification : {CHECK_INTERVAL} secondes", flush=True)

    last_mtime = None
    if SESSION_FILE.exists():
        last_mtime = SESSION_FILE.stat().st_mtime
        print(f"Session existante détectée (mtime: {last_mtime}). En attente d'une mise à jour...", flush=True)
    else:
        print(f"Fichier de session introuvable : '{SESSION_FILE}'. En attente...", flush=True)

    while True:
        try:
            print(f"[Vérification] Analyse du fichier de session...", flush=True)
            if SESSION_FILE.exists():
                current_mtime = SESSION_FILE.stat().st_mtime

                if last_mtime is not None and current_mtime > last_mtime:
                    print(f"Modification détectée (ancien mtime: {last_mtime} -> nouveau mtime: {current_mtime})", flush=True)
                    run_collection_pipeline()
                    last_mtime = current_mtime
                elif last_mtime is None:
                    last_mtime = current_mtime
                    print(f"Premier fichier pris en compte (mtime: {current_mtime})", flush=True)
                    run_collection_pipeline()
                else:
                    print(f"Aucune modification. En veille pour {CHECK_INTERVAL} secondes...", flush=True)
            else:
                print(f"Fichier de session introuvable : '{SESSION_FILE}'. En attente...", flush=True)

        except Exception as e:
            print(f"Erreur inattendue dans la boucle de surveillance : {e}", flush=True)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    watch_session()