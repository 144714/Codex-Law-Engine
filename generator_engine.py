import os, json, openai, urllib.request, datetime, hashlib, time

# Billion-Dollar Configuration
BASE_PATH = 'Codex_Intelligence'
INDEX_FILE = os.path.join(BASE_PATH, 'global_registry.json')
STATE_FILE = 'engine_state.log'
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def setup_env():
    """הכנת סביבת העבודה"""
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)
        print(f"📁 Created Intelligence Directory")

def get_prime_targets(count=30):
    """משיכת מטרות איכות מרשימת המיליון עם מנגנון שריון רב-שכבתי"""
    rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: rank = int(f.read().strip())
            except: rank = 0
    
    targets = []
    # רשימת מקורות חלופיים לרשימת המיליון
    sources = [
        "https://tranco-list.eu/download/daily/top-1m.csv",
        "https://raw.githubusercontent.com/pytoolz/tranco-list/master/top-1m.csv"
    ]
    
    for url in sources:
        try:
            print(f"📡 Accessing global registry via: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                for i, line in enumerate(resp):
                    if i < rank: continue
                    try:
                        decoded = line.decode('utf-8').strip()
                        if ',' in decoded:
                            domain = decoded.split(',')[1]
                            targets.append({"domain": domain, "rank": i + 1})
                    except: continue
                    if len(targets) >= count: break
            if targets: break
        except Exception as e:
            print(f"⚠️ Source failed: {e}")
            continue

    # Fallback למקרה של תקלה ברשת העולמית
    if not targets:
        print("⚠️ All global sources failed. Using high-value fallback.")
        hardcoded_top = ["google.com", "youtube.com", "apple.com", "microsoft.com", "amazon.com", "netflix.com", "spotify.com", "adobe.com", "instagram.com", "whatsapp.com"]
        targets = [{"domain": d, "rank": rank + i + 1} for i, d in enumerate(hardcoded_top)]

    with open(STATE_FILE, 'w') as f: f.write(str(rank + len(targets)))
    return targets

def build_vault(site, audit):
    """שמירת נתונים במבנה אטומי - הגרסה הסופית"""
    master_index = {}
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f: master_index = json.load(f)
        except: master_index = {}

    for category, laws in audit.items():
        if not isinstance(laws, list): continue
        cat_id = category.lower().replace(" ", "_").strip()
        folder = os.path.join(BASE_PATH, cat_id)
        os.makedirs(folder, exist_ok=True)
        
        file_id = f"{site['domain'].replace('.', '_')}.json"
        
        # בניית רשומת המודיעין
        intel_record = {
            "meta": {
                "rank": site['rank'], 
                "site": site['domain'], 
                "date": TIMESTAMP,
                "integrity_hash": hashlib.md5(str(laws).encode()).hexdigest()
            },
            "data": laws
        }
        
        with open(os.path.join(folder, file_id), 'w', encoding='utf-8') as f:
            json.dump(intel_record, f, indent=2, ensure_ascii=False)
        
        # עדכון האינדקס
        if cat_id not in master_index: master_index[cat_id] = []
        if site['domain'] not in master_index[cat_id]: master_index[cat_id].insert(0, site['domain'])

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)

def execute_vision():
    """הפעלת מנוע ה-Oracle"""
    setup_env()
    targets = get_prime_targets(30)
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ Critical: OpenAI API Key missing.")
        return
        
    client = openai.OpenAI(api_key=api_key)
    
    for target in targets:
        print(f"💎 Deconstructing DNA: {target['domain']} (Rank #{target['rank']})")
        try:
            # AI Logic: Oracle Intelligence Mode
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are the Codex Oracle. Audit the site and return ONLY a JSON. Keys: Architecture, Cyber-Defense, UX-Laws, Brand-DNA. Each category must contain a list of 5 objects: {title, description, technical_spec, severity_score(1-100)}."},
                    {"role": "user", "content": f"Extract Technical DNA: {target['domain']}"}
                ],
                response_format={"type": "json_object"}
            )
            
            audit_result = json.loads(res.choices[0].message.content)
            build_vault(target, audit_result)
            print(f"✅ Vault Updated: {target['domain']}")
            
        except Exception as e: 
            print(f"⚠️ Bypass {target['domain']} due to error: {e}")
            time.sleep(1) # מניעת עומס במקרה של תקלה

if __name__ == "__main__":
    execute_vision()
