import feedparser
import json
import os
from datetime import datetime

# Configuration des sources
FEEDS = [
    {"name": "Opex360", "url": "http://www.opex360.com/feed/"},
    {"name": "Forces Opérations", "url": "https://www.forcesoperations.com/feed/"},
    {"name": "Géopolitique & Défense", "url": "https://www.lemonde.fr/defense/rss_full.xml"},
]

DATA_FILE = "news.json"
MAX_ARTICLES = 50

def fetch_news():
    all_articles = []
    
    # Charger l'existant pour éviter les doublons si besoin (optionnel ici car on écrase/trie)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                old_articles = json.load(f)
            except:
                old_articles = []
    else:
        old_articles = []

    for source in FEEDS:
        print(f"Parsing: {source['name']}...")
        feed = feedparser.parse(source['url'])
        
        for entry in feed.entries:
            # Extraction et nettoyage des données
            published = entry.get('published', entry.get('updated', datetime.now().isoformat()))
            
            article = {
                "title": entry.title,
                "summary": entry.summary.split('<')[0][:200] + "...", # Nettoyage HTML sommaire
                "link": entry.link,
                "date": published,
                "source": source['name'],
                "category": determine_category(entry.title + entry.summary)
            }
            all_articles.append(article)

    # Fusion avec l'ancien, dédoublonnage par lien
    combined = {a['link']: a for a in (old_articles + all_articles)}.values()
    
    # Tri par date décroissante (nécessite une date parseable, sinon reste en string)
    # Pour plus de robustesse, on pourrait parser avec dateutil, mais feedparser normalise souvent bien.
    sorted_articles = sorted(combined, key=lambda x: x['date'], reverse=True)

    # Sauvegarde des N derniers articles
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(sorted_articles)[:MAX_ARTICLES], f, ensure_ascii=False, indent=4)
    
    print(f"Mise à jour terminée : {len(sorted_articles[:MAX_ARTICLES])} articles sauvegardés.")

def determine_category(text):
    """Logique simple de catégorisation par mots-clés"""
    text = text.lower()
    if any(word in text for word in ["avion", "rafale", "air", "f-35"]): return "Air"
    if any(word in text for word in ["char", "blindé", "vbcid", "terre"]): return "Terre"
    if any(word in text for word in ["frégate", "sous-marin", "mer", "marine"]): return "Mer"
    if any(word in text for word in ["cyber", "numérique", "hack"]): return "Cyber"
    return "Général"

if __name__ == "__main__":
    fetch_news()
