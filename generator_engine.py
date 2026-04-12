import os, json, openai, urllib.request, datetime, hashlib, time

# Billion-Dollar Configuration
BASE_PATH = 'Codex_Intelligence'
INDEX_FILE = os.path.join(BASE_PATH, 'global_registry.json')
STATE_FILE = 'engine_state.log'
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def get_prime_targets(count=30):
    """משיכת מטרות איכות מרשימת המיליון עם Fail-Safe"""
    rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: rank = int(f.read().strip())
            except: rank = 0
    
    targets = []
    try:
        url = "https://tranco-list.eu/download/daily/top-1m.csv"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            for i, line in enumerate(resp):
                if i < rank: continue
                domain = line.decode('utf-8').strip().split(',')[1]
                targets.append({"domain": domain, "rank": i + 1})
                if len(targets) >= count: break
        with open(STATE_FILE, 'w') as f: f.write(str(rank + count))
    except: targets = [{"domain": "openai.com", "rank": 999}]
    return targets

def build_vault(site, audit):
    """שמירת נתונים במבנה אטומי למניעת התנגשויות (High Scale)"""
    master_index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f: master_index = json.load(f)

    for category, laws in audit.items():
        if not isinstance(laws, list): continue
        cat_id = category.lower().replace(" ", "_")
        folder = os.path.join(BASE_PATH, cat_id)
        os.makedirs(folder, exist_ok=True)
        
        file_id = f"{site['domain'].replace('.', '_')}.json"
        with open(os.path.join(folder, file_id), 'w', encoding='utf-8') as f:
            json.dump({
                "meta": {"rank": site['rank'], "site": site['domain'], "date": TIMESTAMP},
                "data": laws
            }, f, indent=2, ensure_ascii=False)
        
        if cat_id not in master_index: master_index[cat_id] = []
        if site['domain'] not in master_index[cat_id]: master_index[cat_id].insert(0, site['domain'])

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)

def execute_vision():
    targets = get_prime_targets(30)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    for target in targets:
        print(f"💎 Analyzing High-Value Target: {target['domain']}")
        try:
            # AI Engineering: Extraction of pure technical DNA
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are the Codex Oracle. Audit the site and return ONLY a JSON. Keys: Architecture, Cyber-Defense, UX-Laws, Brand-DNA. Each must be a list of 5 objects: {title, description, technical_spec, severity_score(1-100)}."},
                    {"role": "user", "content": f"Deconstruct DNA: {target['domain']}"}
                ],
                response_format={"type": "json_object"}
            )
            build_vault(target, json.loads(res.choices[0].message.content))
        except Exception as e: print(f"⚠️ Bypass {target['domain']}: {e}")

if __name__ == "__main__":
    execute_vision()
