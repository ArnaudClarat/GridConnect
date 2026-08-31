import sys, os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from gridconnect.auth.session import SessionManager
from gridconnect.client import OresApiClient
from gridconnect.db import DBStore
from login import *


def main():
    capture_myores_session()

    # Charger la session depuis config/session.json
    session_manager = SessionManager(session_filepath="config/session.json")
    session = session_manager.load_session()

    if not session:
        print("Aucune session trouvée dans 'config/session.json'.")
        print("Veuillez d'abord exécuter 'python scripts/login.py' pour vous authentifier.")
        sys.exit(1)

    print(f"🔑 Session chargée avec succès (site_id: {session.site_id}, source_id: {session.source_id})")

    # Initialiser le client HTTP
    ean = os.getenv("ORES_EAN")
    if not ean:
        print("Erreur : La variable d'environnement ORES_EAN est manquante.")
        return
    
    client = OresApiClient(session=session)
    db = DBStore()

    # Définir la plage de dates
    now = datetime.now(timezone.utc)
    last_ts = db.get_last_timestamp()

    date_debut = last_ts if last_ts else datetime(now.year -2 , 1, 1, 0, 0, 0)
    date_fin = now

    if date_debut >= now:
        print("Base de données déjà à jour. Aucune requête API nécessaire.")
        sys.exit(0)

    print(f"📡 Interrogation de l'API myORES pour le {date_debut.strftime('%Y-%m-%d')}...")

    # Exécuter la requête
    try:
        mesures = client.fetch_measures(start_date=date_debut, end_date=date_fin)
        print(f"{len(mesures)} mesures récupérées !")

        if not mesures:
            print("Aucune mesure renvoyée par l'API pour cette période.")
            sys.exit(0)

        # Afficher les 5 premiers résultats pour validation
        print("\nAperçu des 5 premières mesures :")
        for m in mesures[:5]:
            print(f"  • {m.timestamp} | {m.register.value:<20} | {m.volume_kwh:.3f} kWh (Puissance moyenne: {m.power_kw:.3f} kW)")
    
        print("Enregistrement dans TimescaleDB...")
        inserted_count = DBStore().save_measures(mesures)
    
        print(f"Succès ! {inserted_count} nouvelles mesures insérées en base (les doublons ont été ignorés).")

    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")

if __name__ == "__main__":
    main()