#!/usr/bin/env python3
"""
AGENT 2 - Maillage interne automatique
Ajoute en bas de chaque article une section "A lire aussi" pointant vers
3 autres articles, en reutilisant le style du site (classes .posts/.post).
"""

import json
import re
from pathlib import Path

BLOG_DIR = Path("blog")
INDEX_FILE = Path("scripts/articles_index.json")
MARKER_START = "<!-- MAILLAGE_START -->"
MARKER_END = "<!-- MAILLAGE_END -->"


def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def pick_related(current_slug, all_articles, n=3):
    others = [a for a in all_articles if a["slug"] != current_slug]
    others = sorted(others, key=lambda x: x["date"], reverse=True)
    return others[:n]


def build_html(related):
    if not related:
        return ""
    cards = ""
    for a in related:
        cards += f"""
        <a class="post" href="/blog/{a['slug']}.html">
          <div class="body">
            <span class="cat">Conseils</span>
            <h3>{a['title']}</h3>
          </div>
        </a>"""
    return f"""{MARKER_START}
    <div class="section-head" style="margin-top:3rem">
      <p class="eyebrow">A lire aussi</p>
      <h2>Autres conseils plomberie</h2>
    </div>
    <div class="posts">{cards}
    </div>
    {MARKER_END}"""


def inject(article_path, block):
    html = article_path.read_text(encoding="utf-8")
    if MARKER_START in html and MARKER_END in html:
        html = re.sub(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
                      block, html, flags=re.DOTALL)
    else:
        # Inserer juste avant le footer du site
        if '<footer class="site-foot">' in html:
            html = html.replace('<footer class="site-foot">',
                                f'<section><div class="wrap">{block}</div></section>\n<footer class="site-foot">', 1)
        elif "</body>" in html:
            html = html.replace("</body>", f"{block}\n</body>", 1)
        else:
            html += block
    article_path.write_text(html, encoding="utf-8")


def run():
    articles = load_index()
    if len(articles) < 2:
        print("Moins de 2 articles : maillage inutile pour l'instant")
        return
    count = 0
    for a in articles:
        p = BLOG_DIR / f"{a['slug']}.html"
        if not p.exists():
            continue
        inject(p, build_html(pick_related(a["slug"], articles)))
        count += 1
    print(f"Maillage interne mis a jour sur {count} articles")


if __name__ == "__main__":
    print("Agent maillage interne")
    run()
