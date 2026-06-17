#!/usr/bin/env python3
"""
Agent IA - Generateur d'articles SEO pour chabrier-plomberie.fr
Design synchronise avec le nouveau site (header sticky petrole, footer moderne,
bouton appel mobile, polices Archivo+Inter, couleurs petrole/cuivre).
"""

import anthropic
import os
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

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
    repl = {"à":"a","á":"a","â":"a","ã":"a","ä":"a","å":"a","è":"e","é":"e",
            "ê":"e","ë":"e","ì":"i","í":"i","î":"i","ï":"i","ò":"o","ó":"o",
            "ô":"o","õ":"o","ö":"o","ù":"u","ú":"u","û":"u","ü":"u","ç":"c"}
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

Contexte : {SITE_NAME}, plombier artisan a {CITY} (78), intervient dans {ZONE}. Tel : {PHONE_DISPLAY}.
Audience : particuliers du Mantois.

INSTRUCTIONS STRICTES :
1. Reponds UNIQUEMENT avec du HTML, rien d'autre (pas de triple backtick, pas de preambule)
2. Genere SEULEMENT le contenu interieur (commence par le commentaire META puis le contenu)
3. N'inclus PAS html/head/body ni header/footer (geres automatiquement)
4. Utilise des styles INLINE coherents avec la charte (couleurs : petrole #0F3640, cuivre #BC6638, texte #0F3640). Polices : titres en 'Archivo', texte en 'Inter'.
5. Structure EXACTE :

<!-- META: {{"title": "...", "description": "...", "keywords": "...", "slug": "..."}} -->
<p style="font-family:'Archivo';font-weight:700;text-transform:uppercase;letter-spacing:1.5px;font-size:13px;color:#BC6638;margin:0 0 12px;">Conseils plomberie</p>
<h1 style="font-family:'Archivo';font-weight:800;font-size:clamp(28px,5vw,42px);line-height:1.1;color:#0F3640;margin:0 0 16px;">[Titre H1, 50-60 car., mot-cle au debut]</h1>
<p style="font-size:14px;color:#5a6b6f;margin:0 0 28px;">[date FR] · [X] min de lecture</p>
<p style="font-size:18px;line-height:1.7;color:#2c3e42;margin:0 0 28px;font-weight:500;">[Introduction accrocheuse 2-3 phrases]</p>

<!-- 5 a 7 sections : pour chaque section -->
<h2 style="font-family:'Archivo';font-weight:700;font-size:clamp(22px,3.5vw,28px);color:#0F3640;margin:36px 0 14px;">[Sous-titre]</h2>
<p style="font-size:16px;line-height:1.8;color:#333;margin:0 0 16px;">[paragraphe]</p>
<!-- listes si pertinent : <ul style="font-size:16px;line-height:1.8;color:#333;padding-left:22px;margin:0 0 16px;"><li>...</li></ul> -->

CRITERES SEO :
- Title 50-60 car., meta description 150-160 car. (dans META)
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
    return f'''<header style="position:sticky;top:0;z-index:50;background:rgba(15,54,64,0.92);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,0.08);">
  <div style="max-width:1200px;margin:0 auto;padding:13px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;">
    <a href="/" style="display:flex;align-items:center;gap:11px;">
      <span style="width:38px;height:38px;border-radius:10px;background:linear-gradient(145deg,#D67E47,#BC6638);display:flex;align-items:center;justify-content:center;font-family:'Archivo';font-weight:800;color:#0A262E;font-size:19px;box-shadow:0 4px 14px rgba(188,102,56,0.35);">C</span>
      <span style="display:flex;flex-direction:column;line-height:1.05;">
        <span style="font-family:'Archivo';font-weight:800;font-size:16px;color:#fff;letter-spacing:0.2px;">Chabrier Plomberie</span>
        <span style="font-size:11px;color:#D67E47;font-weight:600;letter-spacing:0.4px;">Artisan plombier &middot; Mantois (78)</span>
      </span>
    </a>
    <div style="display:flex;align-items:center;gap:26px;">
      <nav class="only-desktop" style="display:flex;align-items:center;gap:24px;font-weight:600;font-size:14.5px;color:#EAF1F2;">
        <a href="/services.html">Services</a>
        <a href="/blog/">Conseils</a>
        <a href="/contact.html">Contact</a>
      </nav>
      <a href="tel:{PHONE_TEL}" style="display:flex;align-items:center;gap:9px;background:linear-gradient(145deg,#D67E47,#BC6638);color:#0A262E;font-family:'Archivo';font-weight:700;font-size:15px;padding:11px 18px;border-radius:999px;box-shadow:0 6px 18px rgba(188,102,56,0.4);white-space:nowrap;">
        <span style="font-size:16px;">&#128222;</span><span>{PHONE_DISPLAY}</span>
      </a>
    </div>
  </div>
</header>'''


def _footer():
    return f'''<footer style="background:#071c22;color:#9FB3B7;">
  <div style="max-width:1200px;margin:0 auto;padding:clamp(44px,6vw,68px) 20px clamp(30px,4vw,40px);">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:34px;margin-bottom:40px;">
      <div>
        <div style="display:flex;align-items:center;gap:11px;margin-bottom:16px;">
          <span style="width:38px;height:38px;border-radius:10px;background:linear-gradient(145deg,#D67E47,#BC6638);display:flex;align-items:center;justify-content:center;font-family:'Archivo';font-weight:800;color:#0A262E;font-size:19px;">C</span>
          <span style="font-family:'Archivo';font-weight:800;font-size:17px;color:#fff;">Chabrier Plomberie</span>
        </div>
        <p style="font-size:14px;line-height:1.6;margin:0;max-width:34ch;">Artisan plombier de proximite. Travail soigne, prix annonce d'avance, sans surprise.</p>
      </div>
      <div>
        <div style="font-family:'Archivo';font-weight:700;font-size:14px;color:#fff;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;">Contact</div>
        <a href="tel:{PHONE_TEL}" style="display:flex;align-items:center;gap:9px;font-size:16px;color:#fff;font-weight:600;margin-bottom:12px;">&#128222; {PHONE_DISPLAY}</a>
        <a href="mailto:{EMAIL}" style="display:flex;align-items:center;gap:9px;font-size:14.5px;margin-bottom:12px;word-break:break-all;">&#9993; {EMAIL}</a>
        <div style="display:flex;align-items:center;gap:9px;font-size:14.5px;">&#128205; {CITY} (78)</div>
      </div>
      <div>
        <div style="font-family:'Archivo';font-weight:700;font-size:14px;color:#fff;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:16px;">Zone d'intervention</div>
        <p style="font-size:14px;line-height:1.7;margin:0;">Mantes-la-Jolie &middot; Mantes-la-Ville &middot; Limay &middot; Buchelay &middot; Magnanville &middot; Rosny-sur-Seine &middot; Guerville &middot; Epone</p>
      </div>
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:22px;display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;font-size:13px;">
      <span>&copy; {datetime.now().year} Chabrier Plomberie &mdash; Tous droits reserves.</span>
      <div style="display:flex;gap:18px;">
        <a href="/services.html">Services</a>
        <a href="/blog/">Conseils</a>
        <a href="/contact.html">Contact</a>
        <a href="/mentions-legales.html">Mentions legales</a>
      </div>
    </div>
  </div>
</footer>
<a href="tel:{PHONE_TEL}" class="only-mobile" style="position:fixed;left:0;right:0;bottom:0;z-index:60;background:linear-gradient(145deg,#D67E47,#BC6638);color:#0A262E;font-family:'Archivo';font-weight:800;font-size:18px;padding:16px;align-items:center;justify-content:center;gap:10px;box-shadow:0 -4px 20px rgba(0,0,0,0.25);">
  <span style="font-size:20px;">&#128222;</span> Appeler le {PHONE_DISPLAY}
</a>'''


GLOBAL_CSS = '''*{box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{margin:0;font-family:'Inter',system-ui,sans-serif;color:#0F3640;background:#F6F3EE;-webkit-font-smoothing:antialiased;}
a{text-decoration:none;color:inherit;}
img{display:block;max-width:100%;}
.only-mobile{display:none;}
.pad-mobile{padding-bottom:0;}
@media (max-width:760px){
  .only-mobile{display:flex;}
  .only-desktop{display:none;}
  .pad-mobile{padding-bottom:74px;}
}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto;}}'''


def _head(title, desc, canonical, schema=""):
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
{schema}
<style>{GLOBAL_CSS}</style>'''


def wrap_in_page(article_html, meta):
    today_iso = datetime.now().strftime("%Y-%m-%d")
    schema = f'''<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{meta['title']}","description":"{meta['description']}","author":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}"}},"publisher":{{"@type":"Organization","name":"{SITE_NAME}","url":"{SITE_URL}"}},"datePublished":"{today_iso}","dateModified":"{today_iso}","mainEntityOfPage":"{SITE_URL}/blog/{meta['slug']}.html"}}
</script>'''
    cta = f'''<div style="margin:44px 0;padding:32px;border-radius:16px;background:linear-gradient(145deg,#0F3640,#0A262E);color:#fff;">
  <div style="font-family:'Archivo';font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:1.5px;color:#D67E47;margin-bottom:10px;">Une urgence ?</div>
  <h2 style="font-family:'Archivo';font-weight:800;font-size:24px;color:#fff;margin:0 0 10px;">Besoin d'un plombier dans {ZONE} ?</h2>
  <p style="font-size:15px;line-height:1.6;color:#C5D4D6;margin:0 0 20px;max-width:48ch;">{SITE_NAME} intervient rapidement a {CITY} et dans les communes voisines. Devis gratuit, travail soigne.</p>
  <a href="tel:{PHONE_TEL}" style="display:inline-flex;align-items:center;gap:10px;background:linear-gradient(145deg,#D67E47,#BC6638);color:#0A262E;font-family:'Archivo';font-weight:700;font-size:17px;padding:14px 26px;border-radius:999px;box-shadow:0 6px 18px rgba(188,102,56,0.4);">&#128222; {PHONE_DISPLAY}</a>
</div>'''
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
{_head(meta['title'] + ' &mdash; ' + SITE_NAME, meta['description'], SITE_URL + '/blog/' + meta['slug'] + '.html', schema)}
</head>
<body class="pad-mobile" id="top">
{_header()}
<article style="max-width:760px;margin:0 auto;padding:clamp(32px,5vw,56px) 20px;">
  <p style="font-size:13px;color:#8a9a9e;margin:0 0 24px;"><a href="/" style="color:#BC6638;">Accueil</a> &rsaquo; <a href="/blog/" style="color:#BC6638;">Conseils</a> &rsaquo; {meta['title']}</p>
  {article_html}
  {cta}
</article>
{_footer()}
</body>
</html>'''


def update_blog_index(articles_index):
    cards = ""
    for a in sorted(articles_index, key=lambda x: x["date"], reverse=True):
        cards += f'''
      <a href="/blog/{a['slug']}.html" style="display:block;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(15,54,64,0.08);padding:26px;border:1px solid rgba(15,54,64,0.06);">
        <span style="font-family:'Archivo';font-weight:700;font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#BC6638;">Conseils</span>
        <h2 style="font-family:'Archivo';font-weight:700;font-size:20px;color:#0F3640;margin:10px 0 8px;line-height:1.25;">{a['title']}</h2>
        <p style="font-size:14.5px;line-height:1.6;color:#5a6b6f;margin:0;">{a['description']}</p>
      </a>'''
    schema_head = _head('Conseils plomberie &mdash; ' + SITE_NAME + ' | Plombier ' + CITY,
                        'Conseils et astuces plomberie par ' + SITE_NAME + ', votre plombier a ' + CITY + ' et dans ' + ZONE + '.',
                        SITE_URL + '/blog/')
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
{schema_head}
</head>
<body class="pad-mobile" id="top">
{_header()}
<section style="max-width:1100px;margin:0 auto;padding:clamp(40px,6vw,68px) 20px;">
  <p style="font-family:'Archivo';font-weight:700;text-transform:uppercase;letter-spacing:1.5px;font-size:13px;color:#BC6638;margin:0 0 12px;">Le blog</p>
  <h1 style="font-family:'Archivo';font-weight:800;font-size:clamp(30px,5vw,44px);line-height:1.1;color:#0F3640;margin:0 0 14px;">Conseils &amp; astuces plomberie</h1>
  <p style="font-size:17px;line-height:1.7;color:#5a6b6f;max-width:60ch;margin:0 0 40px;">Guides pratiques pour entretenir, depanner et renover votre plomberie. Et quand il faut un pro, {SITE_NAME} intervient dans {ZONE}.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px;">{cards}
  </div>
</section>
{_footer()}
</body>
</html>'''
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
              ("/contact.html", "0.8", "monthly"),
              ("/mentions-legales.html", "0.2", "yearly"),
              ("/blog/", "0.7", "weekly")]
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
