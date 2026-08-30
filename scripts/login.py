import re
import sys
from pathlib import Path
from datetime import datetime

# Ajout du dossier src/ au path pour importer gridconnect
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from playwright.sync_api import sync_playwright
from gridconnect.auth.session import SessionManager, OresSession


def capture_myores_session():
    session_manager = SessionManager(session_filepath="config/session.json")
    
    found_site_id = None
    found_source_id = None

    print("🚀 Lancement du navigateur pour l'authentification myORES...")
    
    with sync_playwright() as p:
        # Lancement d'une instance Chromium visible (non-headless pour interagir avec itsme)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Écouteur réseau pour intercepter site_id et source_id dans les URLs de l'API
        def handle_request(request):
            nonlocal found_site_id, found_source_id
            # Recherche du pattern: /sites/{site_id}/sources/{source_id}/
            match = re.search(r"/sites/(\d+)/sources/(\d+)/", request.url)
            if match and not (found_site_id and found_source_id):
                found_site_id = match.group(1)
                found_source_id = match.group(2)
                print(f"🎯 Métadonnées détectées -> site_id: {found_site_id}, source_id: {found_source_id}")

        page.on("request", handle_request)

        # Naviguer vers la page d'accueil myORES
        print("🌐 Ouverture de https://maconso.myores.be...")
        page.goto("https://maconso.myores.be")

        print("\n👉 Veuillez effectuer la connexion via itsme dans la fenêtre du navigateur.")
        print("⏳ Attente de la détection du cookie de session 'ores-prod-auth'...\n")

        # Boucle d'attente jusqu'à détection du cookie après connexion
        auth_cookie_value = None
        while not auth_cookie_value:
            cookies = context.cookies()
            for cookie in cookies:
                if cookie["name"] == "ores-prod-auth":
                    auth_cookie_value = cookie["value"]
                    break
            page.wait_for_timeout(1000)

        print("✅ Cookie 'ores-prod-auth' capturé avec succès !")

        # Attente de 3 secondes supplémentaires pour s'assurer que les requêtes d'API réseau capturent site/source
        page.wait_for_timeout(3000)

        # Construction et sauvegarde de la session
        session = OresSession(
            auth_cookie=auth_cookie_value,
            created_at=datetime.now(),
            site_id=found_site_id,
            source_id=found_source_id
        )

        session_manager.save_session(session)
        print(f"💾 Session enregistrée dans '{session_manager.session_filepath}'")

        browser.close()

if __name__ == "__main__":
    capture_myores_session()