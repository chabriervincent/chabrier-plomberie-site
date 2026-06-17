#!/usr/bin/env python3
"""
AGENT 4 — Audit technique SEO
─────────────────────────────────────────
Vérifie la santé SEO de chaque article et produit un rapport.
Détecte les problèmes qui empêchent de bien remonter dans Google :
  - Title trop court / trop long
  - Meta description manquante ou mauvaise longueur
  - Absence de H1 ou plusieurs H1
  - Images sans attribut alt
  - Contenu trop court (< 600 mots)
  - Liens internes manquants

Ne modifie rien : produit un rapport pour que tu saches quoi corriger.
"""

import re
from pathlib import Path

BLOG_DIR = Path("blog")

# Seuils recommandés
TITLE_MIN, TITLE_MAX = 30, 65
DESC_MIN, DESC_MAX = 120, 160
MIN_WORDS = 600


def audit_article(path):
    """Audite un fichier HTML et retourne la liste des problèmes."""
    html = path.read_text(encoding="utf-8")
    issues = []

    # Title
    title_match = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    if not title_match:
        issues.append("❌ Balise <title> manquante")
    else:
        title = title_match.group(1).strip()
        if len(title) < TITLE_MIN:
            issues.append(f"⚠️ Title trop court ({len(title)} car., visez {TITLE_MIN}-{TITLE_MAX})")
        elif len(title) > TITLE_MAX:
            issues.append(f"⚠️ Title trop long ({len(title)} car., visez {TITLE_MIN}-{TITLE_MAX})")

    # Meta description
    desc_match = re.search(r'<meta name="description" content="(.*?)"', html, re.DOTALL)
    if not desc_match:
        issues.append("❌ Meta description manquante")
    else:
        desc = desc_match.group(1).strip()
        if len(desc) < DESC_MIN:
            issues.append(f"⚠️ Meta description courte ({len(desc)} car., visez {DESC_MIN}-{DESC_MAX})")
        elif len(desc) > DESC_MAX:
            issues.append(f"⚠️ Meta description longue ({len(desc)} car., visez {DESC_MIN}-{DESC_MAX})")

    # H1
    h1_count = len(re.findall(r"<h1[\s>]", html))
    if h1_count == 0:
        issues.append("❌ Aucun H1")
    elif h1_count > 1:
        issues.append(f"⚠️ {h1_count} balises H1 (une seule recommandée)")

    # Images sans alt
    imgs = re.findall(r"<img[^>]*>", html)
    imgs_no_alt = [i for i in imgs if "alt=" not in i]
    if imgs_no_alt:
        issues.append(f"⚠️ {len(imgs_no_alt)} image(s) sans attribut alt")

    # Nombre de mots (texte visible approximatif)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    word_count = len(text.split())
    if word_count < MIN_WORDS:
        issues.append(f"⚠️ Contenu court (~{word_count} mots, visez {MIN_WORDS}+)")

    # Liens internes
    internal_links = re.findall(r'href="(/[^"]*)"', html)
    blog_links = [l for l in internal_links if "/blog/" in l]
    if len(blog_links) < 1:
        issues.append("⚠️ Aucun lien interne vers un autre article (maillage)")

    # Canonical
    if 'rel="canonical"' not in html:
        issues.append("⚠️ Balise canonical manquante")

    # Données structurées
    if "application/ld+json" not in html:
        issues.append("⚠️ Pas de données structurées (Schema.org)")

    return issues, word_count


def run():
    """Audite tous les articles et affiche un rapport."""
    if not BLOG_DIR.exists():
        print("ℹ️ Dossier blog/ introuvable")
        return

    articles = sorted(BLOG_DIR.glob("*.html"))
    articles = [a for a in articles if a.name != "index.html"]

    if not articles:
        print("ℹ️ Aucun article à auditer")
        return

    print(f"🔍 Audit SEO de {len(articles)} article(s)\n")
    print("=" * 60)

    total_issues = 0
    clean = 0

    for path in articles:
        issues, words = audit_article(path)
        total_issues += len(issues)
        if not issues:
            clean += 1
            print(f"\n✅ {path.name} ({words} mots) — RAS")
        else:
            print(f"\n📄 {path.name} ({words} mots)")
            for issue in issues:
                print(f"   {issue}")

    print("\n" + "=" * 60)
    print(f"📊 Bilan : {clean}/{len(articles)} articles sans problème")
    print(f"   {total_issues} point(s) d'amélioration au total")

    if total_issues == 0:
        print("🎉 Tous les articles sont SEO-clean !")


if __name__ == "__main__":
    print("🩺 Agent audit technique SEO")
    run()
