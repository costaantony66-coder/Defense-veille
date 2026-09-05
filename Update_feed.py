import feedparser
import json
import os
from datetime import datetime
from time import mktime
from email.utils import parsedate_tz

# Configuration des sources
FEEDS = [
    {"name": "Opex360", "url": "http://www.opex360.com/feed/"},
    {"name": "Forces Opérations", "url": "https://www.forcesoperations.com/feed/"},
    {"name": "Géopolitique & Défense", "url": "https://www.lemonde.fr/defense/rss_full.xml"},
]

DATA_FILE = "news.json"
MAX_ARTICLES = 50

def parse_entry_date(entry):
    """Convertit proprement la date d'un flux RSS en objet datetime, avec fallback."""
    for field in ('published_parsed', 'updated_parsed'):
        time_struct = entry.get(field)
        if time_struct:
            try:
                return datetime.fromtimestamp(mktime(time_struct))
            except Exception:
                pass
    
    # Fallback sur les chaînes de caractères si les objets parsed n'existent pas
    date_str = entry.get('published', entry.get('updated', ''))
    if date_str:
        try:
            parsed_tuple = parsedate_tz(date_str)
            if parsed_tuple:
                return datetime.fromtimestamp(mktime(parsed_tuple[:9]))
        except Exception:
            pass
            
    return datetime.now()

def fetch_news():
    all_articles = []
    
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
            dt = parse_entry_date(entry)
            
            # Nettoyage HTML sommaire du résumé
            summary_raw = entry.get('summary', '')
            clean_summary = summary_raw.split('<')[0][:200] + "..." if summary_raw else ""
            
            article = {
                "title": entry.get('title', 'Sans titre'),
                "summary": clean_summary,
                "link": entry.get('link', '#'),
                "date": dt.isoformat(), # Stockage propre au format ISO
                "source": source['name'],
                "category": determine_category(entry.get('title', '') + " " + summary_raw)
            }
            all_articles.append(article)

    # Fusion avec l'ancien, dédoublonnage par lien
    combined = {a['link']: a for a in (old_articles + all_articles)}.values()
    
    # Tri précis par date décroissante basé sur le datetime ISO
    sorted_articles = sorted(combined, key=lambda x: x['date'], reverse=True)

    # Sauvegarde des N derniers articles
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(sorted_articles)[:MAX_ARTICLES], f, ensure_ascii=False, indent=4)
    
    print(f"Mise à jour terminée : {len(sorted_articles[:MAX_ARTICLES])} articles sauvegardés.")

def determine_category(text):
    """Logique simple de catégorisation par mots-clés"""
    text = text.lower()
    if any(word in text for word in ["avion", "rafale", "air", "f-35", "chasseur", "drone"]): return "Air"
    if any(word in text for word in ["char", "blindé", "vbcid", "terre", "militaire", "arme", "soldat"]): return "Terre"
    if any(word in text for word in ["frégate", "sous-marin", "mer", "marine", "porte-avions"]): return "Mer"
    if any(word in text for word in ["cyber", "numérique", "hack", "données"]): return "Cyber"
    return "Général"

if __name__ == "__main__":
    fetch_news()
    
