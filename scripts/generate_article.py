#!/usr/bin/env python3
"""
Agent IA - Generateur d'articles SEO pour chabrier-plomberie.fr
Adapte a l'identite visuelle reelle du site (CSS /css/style.css, polices
Archivo + Inter, classes .wrap / .site-head / .post, coordonnees reelles).
"""

import anthropic
import os
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# Configuration entreprise (depuis le site reel)
SITE_NAME = "Chabrier Plomberie"
SITE_URL = "https://chabrier-plomberie.fr"
PHONE_DISPLAY = "06 11 46 00 41"
PHONE_TEL = "+33611460041"
EMAIL = "chabrier.plomberie@gmail.com"
CITY = "Mantes-la-Ville"
ZONE = "le Mantois"
ADDRESS = "166 route de Houdan, 78711 Mantes-la-Ville"

BLOG_DIR = Path("blog")
TOPICS_FILE = Path("scripts/topics.json")
INDEX_FILE = Path("scripts/articles_index.json")

DEFAULT_TOPICS = [
    "Comment deboucher une canalisation bouchee soi-meme",
    "Fuite robinet : causes et solutions rapides",
    "Chauffe-eau qui ne chauffe plus : que faire ?",
    "Changer un joint de robinet : guide etape par etape",
    "WC bouche : astuces pour deboucher sans plombier",
    "Detartrage chauffe-eau : pourquoi et comment ?",
    "Fuite sous l'evier : identifier et reparer",
    "Pression d'eau insuffisante : causes et solutions",
]


def load_topics():
    if TOPICS_FILE.exists():
        with open(TOPICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("remaining", []), data.get("used", [])
    return DEFAULT_TOPICS.copy(), []


def save_topics(remaining, used):
    TOPICS_FILE.parent.mkdir(exist_ok=True)
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump({"remaining": remaining, "used": used}, f, ensure_ascii=False, indent=2)


def slugify(text):
    text = text.lower()
    for a, b in [("aaaaaa", "a"), ("eeee", "e"), ("iiii", "i"),
                 ("ooooo", "o"), ("uuuu", "u"), ("c", "c")]:
        pass
    repl = {"à":"a","á":"a","â":"a","ã":"a","ä":"a","å":"a",
            "è":"e","é":"e","ê":"e","ë":"e","ì":"i","í":"i","î":"i","ï":"i",
            "ò":"o","ó":"o","ô":"o","õ":"o","ö":"o","ù":"u","ú":"u","û":"u","ü":"u","ç":"c"}
    for k, v in repl.items():
        text = text.replace(k, v)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:80]


def generate_article(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""Tu es un expert SEO et redacteur specialise en plomberie.
Genere le CORPS d'un article de blog HTML optimise SEO.

Sujet : {topic}

Contexte entreprise :
- {SITE_NAME}, plombier artisan base a {CITY} (78), intervient dans {ZONE}
- Telephone : {PHONE_DISPLAY}
- Audience : particuliers du Mantois cherchant conseils ou plombier

INSTRUCTIONS STRICTES :
1. Reponds UNIQUEMENT avec du HTML, rien d'autre (pas de triple backtick, pas de preambule)
2. Genere SEULEMENT le contenu interieur (commence par le commentaire META puis le contenu)
3. N'inclus PAS html/head/body ni header/footer du site (geres automatiquement)
4. Utilise UNIQUEMENT ces classes CSS du site : eyebrow, section-head, btn, btn-call, faq
5. Structure EXACTE a produire :

<!-- META: {{"title": "...", "description": "...", "keywords": "...", "slug": "..."}} -->
<article class="post-full">
  <p class="eyebrow">Conseils plomberie</p>
  <h1>[Titre H1, 50-60 caracteres, mot-cle au debut]</h1>
  <p class="post-meta"><time datetime="[YYYY-MM-DD]">[date FR]</time> - [X] min de lecture</p>
  <p class="lede-article">[Introduction accrocheuse, 2-3 phrases]</p>
  <h2>[Sous-titre]</h2>
  <p>...</p>
  <ul><li>...</li></ul>
  <h2>Questions frequentes</h2>
  <div class="faq">
    <details open><summary>[Question]</summary><p>[Reponse]</p></details>
    <details><summary>[Question]</summary><p>[Reponse]</p></details>
  </div>
  <div class="article-cta">
    <h2>Besoin d'un plombier dans {ZONE} ?</h2>
    <p>{SITE_NAME} intervient rapidement a {CITY} et dans les communes voisines. Devis gratuit, travail soigne.</p>
    <a class="btn btn-call" href="tel:{PHONE_TEL}">Appeler {PHONE_DISPLAY}</a>
  </div>
</article>

CRITERES SEO :
- Title 50-60 car., meta description 150-160 car. (dans le commentaire META)
- Minimum 800 mots, ton expert et rassurant
- Mentionner {CITY} / {ZONE} naturellement
- 5 a 7 sections h2 de 150-250 mots
Genere maintenant :"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def extract_meta(html_content):
    match = re.search(r"<!-- META: ({.*?}) -->", html_content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html_content, re.DOTALL)
    title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else "Conseil plomberie"
    return {"title": title,
            "description": f"{title} - Conseils par {SITE_NAME}, plombier a {CITY}.",
            "keywords": f"plomberie, plombier {CITY}, {ZONE}",
            "slug": slugify(title)}


def _header():
    return f"""<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/"><span class="mark">&#8984;</span> {SITE_NAME}</a>
    <button class="nav-toggle" aria-label="Menu" onclick="document.getElementById('nav').classList.toggle('open')">&#9776;</button>
    <nav class="nav" id="nav">
      <a href="/services.html">Services</a>
      <a href="/depannage-urgence.html">Depannage urgent</a>
      <a href="/zone-intervention.html">Zone d'intervention</a>
      <a href="/blog/">Conseils</a>
      <a href="/contact.html">Contact</a>
      <a class="btn btn-call" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
    </nav>
  </div>
</header>"""


def _footer():
    return f"""<footer class="site-foot">
  <div class="wrap">
    <div class="grid">
      <div>
        <div class="brand" style="color:#fff"><span class="mark">&#8984;</span> {SITE_NAME}</div>
        <p>Votre plombier artisan a {CITY} et dans tout {ZONE} (78).</p>
      </div>
      <div>
        <h4>Services</h4>
        <a href="/services.html">Fuite et debouchage</a>
        <a href="/services.html">Chauffe-eau</a>
        <a href="/depannage-urgence.html">Depannage urgent</a>
      </div>
      <div>
        <h4>Contact</h4>
        <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <a href="/contact.html">Demander un devis</a>
      </div>
    </div>
    <div class="foot-bottom">
      <span>&copy; {datetime.now().year} {SITE_NAME} - {ADDRESS}</span>
      <span>Plombier {CITY} - Mantois - Yvelines</span>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE_TEL}">Appeler - {PHONE_DISPLAY}</a>"""


def _head(title, desc, canonical):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">"""


def wrap_in_page(article_html, meta):
    today_iso = datetime.now().strftime("%Y-%m-%d")
    schema = f"""<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{meta['title']}","description":"{meta['description']}","author":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}"}},"publisher":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}"}},"datePublished":"{today_iso}","dateModified":"{today_iso}","mainEntityOfPage":"{SITE_URL}/blog/{meta['slug']}.html"}}
</script>"""
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
{_head(meta['title'] + ' - ' + SITE_NAME, meta['description'], SITE_URL + '/blog/' + meta['slug'] + '.html')}
{schema}
</head>
<body>
{_header()}
<section style="padding-top:2.5rem">
  <div class="wrap" style="max-width:820px">
    <p style="font-size:.85rem;color:var(--muted)"><a href="/">Accueil</a> &rsaquo; <a href="/blog/">Conseils</a> &rsaquo; {meta['title']}</p>
    {article_html}
  </div>
</section>
{_footer()}
</body>
</html>"""


def update_blog_index(articles_index):
    cards = ""
    for a in sorted(articles_index, key=lambda x: x["date"], reverse=True):
        cards += f"""
      <a class="post" href="/blog/{a['slug']}.html">
        <div class="body">
          <span class="cat">Conseils</span>
          <h3>{a['title']}</h3>
          <p>{a['description']}</p>
        </div>
      </a>"""
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
{_head('Conseils plomberie - ' + SITE_NAME + ' | Plombier ' + CITY, 'Conseils et astuces plomberie par ' + SITE_NAME + ', votre plombier a ' + CITY + ' et dans ' + ZONE + '.', SITE_URL + '/blog/')}
</head>
<body>
{_header()}
<section>
  <div class="wrap">
    <div class="section-head">
      <p class="eyebrow">Le blog</p>
      <h2>Conseils et astuces plomberie</h2>
      <p>Guides pratiques pour entretenir, depanner et renover votre plomberie. Et quand il faut un pro, {SITE_NAME} intervient dans {ZONE}.</p>
    </div>
    <div class="posts">{cards}
    </div>
  </div>
</section>
{_footer()}
</body>
</html>"""
    BLOG_DIR.mkdir(exist_ok=True)
    with open(BLOG_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Index blog mis a jour")


def load_articles_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_articles_index(idx):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)


def generate_sitemap(idx):
    today = datetime.now().strftime("%Y-%m-%d")
    static = [("/", "1.0", "weekly"), ("/services.html", "0.9", "monthly"),
              ("/depannage-urgence.html", "0.9", "monthly"),
              ("/zone-intervention.html", "0.8", "monthly"),
              ("/contact.html", "0.8", "monthly"), ("/blog/", "0.7", "weekly")]
    urls = ""
    for p, prio, freq in static:
        urls += f'\n  <url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>'
    for a in sorted(idx, key=lambda x: x["date"], reverse=True):
        urls += f'\n  <url><loc>{SITE_URL}/blog/{a["slug"]}.html</loc><lastmod>{a["date"]}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>'
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}\n</urlset>'
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"sitemap.xml ({len(static) + len(idx)} URLs)")


def generate_robots_txt():
    content = f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    p = Path("robots.txt")
    if not p.exists() or "sitemap.xml" not in p.read_text(encoding="utf-8").lower():
        with open("robots.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("robots.txt mis a jour")
    else:
        print("robots.txt deja OK")


def ping_indexnow():
    key = os.environ.get("INDEXNOW_KEY", "").strip()
    if not key:
        return
    try:
        url = f"https://api.indexnow.org/indexnow?url={urllib.parse.quote(SITE_URL + '/sitemap.xml')}&key={key}"
        req = urllib.request.Request(url, headers={"User-Agent": "ChabrierBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"IndexNow notifie (HTTP {resp.status})")
    except Exception as e:
        print(f"Ping IndexNow non envoye ({e})")


def main():
    print("Agent generateur d'articles SEO - Chabrier Plomberie")
    remaining, used = load_topics()
    if not remaining:
        remaining = DEFAULT_TOPICS.copy()
        used = []
    topic = remaining.pop(0)
    used.append(topic)
    print(f"Sujet : {topic}")
    print("Generation via Claude API...")
    article_html = generate_article(topic)
    meta = extract_meta(article_html)
    print(f"{meta['title']} -> /blog/{meta['slug']}.html")
    full_page = wrap_in_page(article_html, meta)
    BLOG_DIR.mkdir(exist_ok=True)
    article_path = BLOG_DIR / f"{meta['slug']}.html"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(full_page)
    print("Article sauvegarde")
    idx = load_articles_index()
    idx.append({"slug": meta["slug"], "title": meta["title"],
                "description": meta["description"],
                "date": datetime.now().strftime("%Y-%m-%d"),
                "date_fr": datetime.now().strftime("%d/%m/%Y")})
    save_articles_index(idx)
    update_blog_index(idx)
    print("Sitemap et robots...")
    generate_sitemap(idx)
    generate_robots_txt()
    try:
        import agent_internal_links
        print("Maillage interne...")
        agent_internal_links.run()
    except Exception as e:
        print(f"Maillage ignore : {e}")
    try:
        import agent_audit
        issues, words = agent_audit.audit_article(article_path)
        if issues:
            print(f"Audit ({words} mots) - {len(issues)} point(s) :")
            for i in issues:
                print(f"   {i}")
        else:
            print(f"Audit : clean ({words} mots)")
    except Exception as e:
        print(f"Audit ignore : {e}")
    ping_indexnow()
    try:
        import agent_indexing
        print("Indexation Google...")
        agent_indexing.index_urls([f"{SITE_URL}/blog/{meta['slug']}.html"])
    except Exception as e:
        print(f"Indexation ignoree : {e}")
    save_topics(remaining, used)
    print(f"\nPublie : {SITE_URL}/blog/{meta['slug']}.html")


if __name__ == "__main__":
    main()
