import feedparser
import json
import os
from datetime import datetime
from time import mktime
from email.utils import parsedate_tz

FEEDS = [
    {"name": "Opex360", "url": "http://www.opex360.com/feed/"},
    {"name": "Forces Opérations", "url": "https://www.forcesoperations.com/feed/"},
    {"name": "Géopolitique & Défense", "url": "https://www.lemonde.fr/defense/rss_full.xml"},
]

DATA_FILE = "news.json"
MAX_ARTICLES = 50

def parse_entry_date(entry):
    for field in ('published_parsed', 'updated_parsed'):
        time_struct = entry.get(field)
        if time_struct:
            try:
                return datetime.fromtimestamp(mktime(time_struct))
            except Exception:
                pass
    
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
                data = json.load(f)
                # Gère le cas où le JSON est une liste ou un dictionnaire structuré
                old_articles = data.get("articles", []) if isinstance(data, dict) else data
            except:
                old_articles = []
    else:
        old_articles = []

    for source in FEEDS:
        print(f"Parsing: {source['name']}...")
        feed = feedparser.parse(source['url'])
        
        for entry in feed.entries:
            dt = parse_entry_date(entry)
            summary_raw = entry.get('summary', '')
            clean_summary = summary_raw.split('<')[0][:200] + "..." if summary_raw else ""
            
            article = {
                "title": entry.get('title', 'Sans titre'),
                "summary": clean_summary,
                "link": entry.get('link', '#'),
                "date": dt.isoformat(),
                "source": source['name'],
                "category": determine_category(entry.get('title', '') + " " + summary_raw)
            }
            all_articles.append(article)

    combined = {a['link']: a for a in (old_articles + all_articles)}.values()
    sorted_articles = sorted(combined, key=lambda x: x['date'], reverse=True)

    # On structure le JSON avec une métadonnée de dernière mise à jour pour forcer le changement Git
    output_data = {
        "last_updated": datetime.now().isoformat(),
        "articles": list(sorted_articles)[:MAX_ARTICLES]
    }

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    
    print(f"Mise à jour terminée : {len(output_data['articles'])} articles sauvegardés.")

def determine_category(text):
    text = text.lower()
    if any(word in text for word in ["avion", "rafale", "air", "f-35", "chasseur", "drone"]): return "Air"
    if any(word in text for word in ["char", "blindé", "vbcid", "terre", "militaire", "arme", "soldat"]): return "Terre"
    if any(word in text for word in ["frégate", "sous-marin", "mer", "marine", "porte-avions"]): return "Mer"
    if any(word in text for word in ["cyber", "numérique", "hack", "données"]): return "Cyber"
    return "Général"

if __name__ == "__main__":
    fetch_news()
    
