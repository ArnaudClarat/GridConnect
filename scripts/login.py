import re, sys, os, subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Ajout du dossier src/ au path pour importer gridconnect
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from playwright.sync_api import sync_playwright
from gridconnect.auth.session import SessionManager, OresSession


def capture_myores_session(session_manager: SessionManager) -> OresSession:
    
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
        auth_cookie = None
        while not auth_cookie:
            auth_cookie = next(
                (c for c in context.cookies() if c["name"] == "ores-prod-auth"), None
            )
            page.wait_for_timeout(1000)

        auth_cookie_value = auth_cookie["value"]

        # Diagnostic: print cookie attributes (never the value itself)
        exp = auth_cookie["expires"]  # Unix timestamp, or -1 for a session cookie
        print("Cookie domain  :", auth_cookie["domain"])
        print("Cookie expires :", "session cookie (no fixed expiry)" if exp == -1
              else datetime.fromtimestamp(exp).isoformat())
        print("httpOnly/secure:", auth_cookie["httpOnly"], auth_cookie["secure"])

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
        deploy_to_remote_server()
        browser.close()
        return session

def deploy_to_remote_server():
    disabled = os.getenv("REMOTE_SERVER_ENABLED", "false").lower() != "true"
    if disabled:
        print("ℹ️ Déploiement distant désactivé dans le fichier .env")
        return

    session_file = Path("config/session.json")
    if not session_file.exists():
        print("❌ Impossible de déployer : config/session.json introuvable.")
        return

    user = os.getenv("REMOTE_SERVER_USER")
    host = os.getenv("REMOTE_SERVER_HOST")
    remote_path = os.getenv("REMOTE_SERVER_PATH")

    if not all([user, host, remote_path]):
        print("⚠️ Configuration serveur incomplète dans le fichier .env (REMOTE_SERVER_*)")
        return

    print(f"\n🚀 Transfert du token de session vers {user}@{host}:{remote_path}...")
    
    destination = f"{user}@{host}:{remote_path}"
    cmd = ["scp", str(session_file), destination]

    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("✅ Jeton de session déployé avec succès sur le serveur !")
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec lors du transfert SCP : {e.stderr}")
    except FileNotFoundError:
        print("❌ Erreur : La commande 'scp' n'est pas installée sur cet ordinateur.")

if __name__ == "__main__":
    session_manager = SessionManager(session_filepath="config/session.json")
    capture_myores_session(session_manager)
    deploy_to_remote_server()