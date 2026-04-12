import os, sys, json, openai, hashlib, urllib.request

# קונפיגורציה מרכזית
BASE_PATH = 'Market_Analysis'
INDEX_FILE = os.path.join(BASE_PATH, 'master_index.json')
STATE_FILE = 'last_scanned_rank.txt' # המונה העולמי

def setup_env():
    """מוודא שסביבת העבודה מוכנה"""
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def get_next_targets(count=10):
    """שואב את X האתרים הבאים מרשימת ה-Top 1M העולמית"""
    start_rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: start_rank = int(f.read().strip())
            except: start_rank = 0

    targets = []
    try:
        url = "https://tranco-list.eu/download/daily/top-1m.csv"
        print(f"📡 Downloading global registry. Starting from rank {start_rank + 1}...")
        
        with urllib.request.urlopen(url) as response:
            line_count = 0
            for line in response:
                line_count += 1
                if line_count <= start_rank: continue
                
                domain = line.decode('utf-8').strip().split(',')[1]
                targets.append(domain)
                if len(targets) >= count: break
                
        with open(STATE_FILE, 'w') as f:
            f.write(str(start_rank + count))
    except Exception as e:
        print(f"❌ Network Error: {e}")
    return targets

def save_to_vault(site, audit_data):
    """מקטלג ושומר כל ממצא בתיקייה הנכונה"""
    for category, laws in audit_data.items():
        if not isinstance(laws, list) or not laws: continue
        
        # יצירת תיקייה לקטגוריה
        clean_cat = category.replace(" ", "_").strip()
        cat_dir = os.path.join(BASE_PATH, clean_cat)
        os.makedirs(cat_dir, exist_ok=True)
        
        # שמירת קובץ נפרד לאתר (Scalable Architecture)
        file_path = os.path.join(cat_dir, f"{site.replace('.', '_')}.json")
        entry = {
            "site": site,
            "category": clean_cat,
            "timestamp": "2026-04-12", # תאריך דינמי
            "laws": laws
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        
        # עדכון האינדקס המרכזי
        update_index(site, clean_cat)

def update_index(site, category):
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f: index = json.load(f)
    
    if category not in index: index[category] = []
    if site not in index[category]: index[category].append(site)
    
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

def run_engine():
    setup_env()
    targets = get_next_targets(10) # 10 אתרים בכל הרצה
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in targets:
        print(f"🧬 Auditing: {site}")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a World-Class Auditor. Return ONLY a JSON with keys: UI-Design, Security, UX-Flow, Accessibility. Each must contain a list of objects with: title, description, design_token, remediation."},
                    {"role": "user", "content": f"Extract technical DNA laws for {site}"}
                ],
                response_format={"type": "json_object"}
            )
            audit_result = json.loads(response.choices[0].message.content)
            save_to_vault(site, audit_result)
            print(f"✅ Ingested: {site}")
        except Exception as e:
            print(f"⚠️ Skip {site}: {e}")

if __name__ == "__main__":
    run_engine()
