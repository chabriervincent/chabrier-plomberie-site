#!/usr/bin/env python3
"""
AGENT 1 - Recherche de mots-cles locaux (Mantois prioritaire)
Genere des sujets ciblant la vraie zone d'intervention de Chabrier Plomberie.
Priorite : Mantes-la-Ville et communes voisines, puis elargissement Yvelines.
"""

import json
import itertools
from pathlib import Path

# Coeur de cible : le Mantois (zone reelle d'intervention, fort potentiel)
VILLES_COEUR = [
    "Mantes-la-Ville", "Mantes-la-Jolie", "Limay", "Buchelay",
    "Magnanville", "Rosny-sur-Seine", "Guerville", "Epone",
    "Vert", "Soindres", "Porcheville", "Issou",
]

# Elargissement Yvelines (secondaire, si on veut etendre plus tard)
VILLES_ELARGIES = [
    "Bonnieres-sur-Seine", "Houdan", "Septeuil", "Aubergenville",
    "Les Mureaux", "Meulan-en-Yvelines",
]

SERVICES = [
    "Plombier {ville} : intervention rapide et devis gratuit",
    "Depannage plomberie urgence a {ville}",
    "Debouchage canalisation a {ville} : tarifs et delais",
    "Recherche de fuite d'eau a {ville}",
    "Remplacement chauffe-eau a {ville}",
    "Installation salle de bain a {ville}",
]


def generate_local_topics():
    topics = []
    # Coeur de cible en priorite : on varie les services
    cycle = itertools.cycle(SERVICES)
    for ville in VILLES_COEUR:
        topics.append(next(cycle).format(ville=ville))
    # Elargissement ensuite
    cycle2 = itertools.cycle(SERVICES)
    for ville in VILLES_ELARGIES:
        topics.append(next(cycle2).format(ville=ville))
    return topics


def merge_into_topics_file(topics_file="scripts/topics.json"):
    path = Path(topics_file)
    local = generate_local_topics()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"remaining": [], "used": []}
    existing = set(data["remaining"]) | set(data.get("used", []))
    new = [t for t in local if t not in existing]
    # Intercaler local + generique pour varier
    remaining = data["remaining"]
    merged = []
    li, gi = iter(new), iter(remaining)
    while True:
        added = False
        for it in (li, gi):
            try:
                merged.append(next(it)); added = True
            except StopIteration:
                pass
        if not added:
            break
    data["remaining"] = merged
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(new)} sujets locaux ajoutes - {len(merged)} sujets au total")
    return new


if __name__ == "__main__":
    print("Agent recherche de mots-cles locaux - Mantois")
    print(f"{len(VILLES_COEUR)} communes coeur de cible + {len(VILLES_ELARGIES)} elargies")
    new = merge_into_topics_file()
    print("\nExemples :")
    for t in new[:6]:
        print(f"  - {t}")
