import os, sys, json, openai, hashlib, urllib.request, time

# הגדרות נתיבים (מוחלטות לעבודה בשרת)
BASE_PATH = os.path.join(os.getcwd(), 'Market_Analysis')
INDEX_FILE = os.path.join(BASE_PATH, 'master_index.json')
STATE_FILE = os.path.join(os.getcwd(), 'last_scanned_rank.txt')

def setup_env():
    """הכנת הסביבה הפיזית לשמירת הדאטה"""
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)
        print(f"📁 Created base directory: {BASE_PATH}")

def get_next_targets(count=10):
    """משיכת דומיינים מרשימת ה-Top 1M העולמית עם טיפול בחסימות"""
    start_rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: start_rank = int(f.read().strip())
            except: start_rank = 0

    targets = []
    # רשימת חירום אם השרת החיצוני קורס
    fallback = ["google.com", "youtube.com", "facebook.com", "amazon.com", "apple.com", "netflix.com"]
    
    url = "https://tranco-list.eu/download/daily/top-1m.csv"
    print(f"📡 Accessing global registry. Starting from Rank: {start_rank + 1}")

    try:
        # התחזות לדפדפן כדי למנוע שגיאת 403/404 מהשרת
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            line_count = 0
            for line in response:
                line_count += 1
                if line_count <= start_rank: continue
                
                # עיבוד השורה (פורמט CSV: Rank,Domain)
                decoded_line = line.decode('utf-8').strip()
                if ',' in decoded_line:
                    domain = decoded_line.split(',')[1]
                    targets.append(domain)
                
                if len(targets) >= count: break
                
        # עדכון המונה רק אם הצלחנו למשוך אתרים
        with open(STATE_FILE, 'w') as f:
            f.write(str(start_rank + len(targets)))
            
    except Exception as e:
        print(f"⚠️ External API Error: {e}. Switching to fallback mode.")
        targets = fallback[:count]

    return targets

def save_to_vault(site, audit_result):
    """שמירה מקוטלגת של הממצאים למבנה ה-Database"""
    for category, laws in audit_result.items():
        if not isinstance(laws, list) or not laws: continue
        
        # ניקוי שם הקטגוריה ליצירת תיקייה תקנית
        clean_cat = category.replace(" ", "_").replace("/", "-").strip()
        cat_dir = os.path.join(BASE_PATH, clean_cat)
        os.makedirs(cat_dir, exist_ok=True)
        
        # שמירת קובץ JSON ייחודי לאתר בתוך הקטגוריה
        file_name = f"{site.replace('.', '_')}.json"
        file_path = os.path.join(cat_dir, file_name)
        
        entry = {
            "site": site,
            "category": clean_cat,
            "scanned_at": "2026-04-12", # תאריך סטטי לצורך הפרויקט
            "laws": laws
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, indent=2, ensure_ascii=False)
        
        update_master_index(site, clean_cat)

def update_master_index(site, category):
    """מעדכן את האינדקס המרכזי שמשמש את האתר להצגת התפריטים"""
    index_data = {}
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except: index_data = {}
    
    if category not in index_data:
        index_data[category] = []
    
    if site not in index_data[category]:
        index_data[category].append(site)
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

def run_engine():
    """המנוע הראשי שמפעיל את שרשרת הייצור"""
    setup_env()
    targets = get_next_targets(10) # 10 אתרים בכל הרצה
    
    if not targets:
        print("❌ No targets found. Pipeline aborted.")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Missing OpenAI API Key!")
        return
        
    client = openai.OpenAI(api_key=api_key)

    for site in targets:
        print(f"🧬 Analyzing DNA: {site}...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Senior Web Auditor. Return ONLY a JSON object with 4 keys: UI-Design, Security, UX-Flow, Accessibility. Each key must be a list of 5 objects with: title, description, design_token, remediation."},
                    {"role": "user", "content": f"Audit the site: {site}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            save_to_vault(site, result)
            print(f"✅ Data for {site} ingested and indexed.")
            
        except Exception as e:
            print(f"⚠️ Failed to audit {site}: {e}")
            continue

if __name__ == "__main__":
    run_engine()
