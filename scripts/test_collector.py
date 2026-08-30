import sys
from datetime import datetime, timedelta
from pathlib import Path

# Plus besoin d'ajouter src/ au sys.path si vous avez utilisé 'pip install -e .'
from gridconnect.auth.session import SessionManager
from gridconnect.client import OresApiClient


def main():
    # 1. Charger la session depuis config/session.json
    session_manager = SessionManager(session_filepath="config/session.json")
    session = session_manager.load_session()

    if not session:
        print("❌ Aucune session trouvée dans 'config/session.json'.")
        print("Veuillez d'abord exécuter 'python scripts/login.py' pour vous authentifier.")
        sys.exit(1)

    print(f"🔑 Session chargée avec succès (site_id: {session.site_id}, source_id: {session.source_id})")

    # 2. Initialiser le client HTTP
    # Pour le moment, on met un EAN factice, il sera remplacé plus tard par votre variable d'environnement
    client = OresApiClient(session=session, ean="541449000000000000")

    # 3. Définir la plage de dates (hier de 00:00:00 à 23:59:59)
    # L'API s'attend à une plage horaire, on fixe à hier pour s'assurer d'avoir des données complètes
    now = datetime.now()
    date_debut = datetime(now.year, 1, 1, 0, 0, 0)
    date_fin = now

    print(f"📡 Interrogation de l'API myORES pour le {date_debut.strftime('%Y-%m-%d')}...")

    # 4. Exécuter la requête
    try:
        mesures = client.fetch_measures(start_date=date_debut, end_date=date_fin)
        print(f"✅ Succès : {len(mesures)} mesures récupérées !")

        if not mesures:
            print("Aucune mesure renvoyée par l'API pour cette période.")
            sys.exit(0)

        # 5. Afficher les 5 premiers résultats pour validation
        print("\nAperçu des 5 premières mesures :")
        for m in mesures[:5]:
            print(f"  • {m.timestamp} | {m.register.value:<20} | {m.value_kwh:.3f} kWh (Puissance moyenne: {m.power_kw:.3f} kW)")

    except Exception as e:
        print(f"💥 Erreur lors de la récupération des données : {e}")

if __name__ == "__main__":
    main()