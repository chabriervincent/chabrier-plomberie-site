#!/usr/bin/env python3
"""
AGENT 3 — Indexation automatique (Google Indexing API)
─────────────────────────────────────────
Notifie Google automatiquement à chaque nouvel article, sans avoir à
cliquer "Demander une indexation" manuellement dans Search Console.

⚙️ PRÉREQUIS (à faire une seule fois) :
  1. Aller sur https://console.cloud.google.com
  2. Créer un projet → activer "Indexing API"
  3. Créer un compte de service (Service Account) → télécharger la clé JSON
  4. Dans Search Console : Paramètres → Utilisateurs → ajouter l'email du
     compte de service comme PROPRIÉTAIRE
  5. Mettre le contenu du JSON dans le secret GitHub : GOOGLE_INDEXING_KEY

Si la clé n'est pas configurée, l'agent s'ignore proprement (aucune erreur).

Note : l'Indexing API est officiellement prévue pour les offres d'emploi et
les diffusions en direct, mais elle accélère aussi la découverte d'autres
pages dans la pratique. En complément, le sitemap reste la méthode officielle.
"""

import os
import json
import time
import urllib.request


def get_access_token(service_account_info):
    """
    Obtient un token OAuth2 à partir du compte de service.
    Utilise google-auth si disponible.
    """
    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
    except ImportError:
        print("ℹ️ Bibliothèque google-auth absente — indexation auto ignorée")
        print("   (ajoutez 'google-auth' aux dépendances pour l'activer)")
        return None

    credentials = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/indexing"],
    )
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token


def notify_google(url, token):
    """Envoie une notification URL_UPDATED à Google pour une URL donnée."""
    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    payload = json.dumps({"url": url, "type": "URL_UPDATED"}).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️ Échec notification pour {url} : {e}")
        return False


def index_urls(urls):
    """
    Point d'entrée principal. Reçoit une liste d'URLs à indexer.
    Échoue silencieusement si la clé n'est pas configurée.
    """
    raw_key = os.environ.get("GOOGLE_INDEXING_KEY", "").strip()
    if not raw_key:
        print("ℹ️ GOOGLE_INDEXING_KEY non configurée — indexation auto ignorée")
        print("   L'article sera quand même découvert via le sitemap.")
        return

    try:
        service_account_info = json.loads(raw_key)
    except json.JSONDecodeError:
        print("⚠️ GOOGLE_INDEXING_KEY n'est pas un JSON valide — ignoré")
        return

    token = get_access_token(service_account_info)
    if not token:
        return

    success = 0
    for url in urls:
        if notify_google(url, token):
            print(f"✅ Indexation demandée : {url}")
            success += 1
        time.sleep(1)  # éviter de saturer l'API

    print(f"\n🎯 {success}/{len(urls)} URLs envoyées à Google")


if __name__ == "__main__":
    # Test manuel
    import sys
    test_urls = sys.argv[1:] or ["https://chabrier-plomberie.fr/"]
    print("📤 Agent indexation automatique")
    index_urls(test_urls)
