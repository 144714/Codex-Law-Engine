import os, json, openai, urllib.request, datetime, hashlib, time

# הגדרות מנוע ה-Intelligence
BASE_PATH = 'Codex_Intelligence'
INDEX_FILE = os.path.join(BASE_PATH, 'global_registry.json')
STATE_FILE = 'engine_state.log'
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def setup_env():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def get_prime_targets(count=20): # סורק 20 אתרים לעומק בכל הרצה
    rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: rank = int(f.read().strip())
            except: rank = 0
    
    targets = []
    sources = ["https://tranco-list.eu/download/daily/top-1m.csv"]
    
    for url in sources:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                for i, line in enumerate(resp):
                    if i < rank: continue
                    decoded = line.decode('utf-8').strip()
                    if ',' in decoded:
                        domain = decoded.split(',')[1]
                        targets.append({"domain": domain, "rank": i + 1})
                    if len(targets) >= count: break
            if targets: break
        except: continue

    with open(STATE_FILE, 'w') as f: f.write(str(rank + len(targets)))
    return targets

def build_vault(site, audit):
    master_index = {}
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f: master_index = json.load(f)
        except: master_index = {}

    for category, laws in audit.items():
        if not isinstance(laws, list): continue
        cat_id = category.upper().replace(" ", "_").strip()
        folder = os.path.join(BASE_PATH, cat_id)
        os.makedirs(folder, exist_ok=True)
        
        file_id = f"{site['domain'].replace('.', '_')}.json"
        intel_record = {
            "meta": {"rank": site['rank'], "site": site['domain'], "date": TIMESTAMP, "version": "DeepScan_v4"},
            "data": laws
        }
        
        with open(os.path.join(folder, file_id), 'w', encoding='utf-8') as f:
            json.dump(intel_record, f, indent=2, ensure_ascii=False)
        
        if cat_id not in master_index: master_index[cat_id] = []
        if site['domain'] not in master_index[cat_id]: master_index[cat_id].insert(0, site['domain'])

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)

def execute_vision():
    setup_env()
    targets = get_prime_targets(20) # 20 אתרים - כל אחד מקבל טיפול VIP
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    for target in targets:
        print(f"🔍 Deep Auditing: {target['domain']}")
        try:
            # פרומפט "מטורף" שמכריח את ה-AI להוציא המון דאטה
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": """You are the Codex Oracle. Perform a DEEP technical audit. 
                    Return ONLY a JSON with exactly these 6 categories: 
                    1. VISUAL_ENGINEERING (UI/UX), 
                    2. SECURITY_PROTOCOLS, 
                    3. PERFORMANCE_DNA, 
                    4. ACCESSIBILITY_LAWS, 
                    5. ARCHITECTURAL_PATTERNS,
                    6. CONVERSION_PSYCHOLOGY.
                    Each category must have 6-8 detailed laws. Each law: {title, description, technical_spec, severity_score(1-100)}."""},
                    {"role": "user", "content": f"Deconstruct everything about: {target['domain']}"}
                ],
                response_format={"type": "json_object"}
            )
            build_vault(target, json.loads(res.choices[0].message.content))
            print(f"💎 Data Goldmine Saved: {target['domain']}")
        except Exception as e: print(f"❌ Failure on {target['domain']}: {e}")

if __name__ == "__main__":
    execute_vision()
