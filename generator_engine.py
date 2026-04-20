import os, json, openai, urllib.request, datetime, hashlib, time

# קונפיגורציה מרכזית
BASE_PATH = 'Codex_Intelligence'
INDEX_FILE = os.path.join(BASE_PATH, 'global_registry.json')
STATE_FILE = 'engine_state.log'
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def setup_env():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def get_prime_targets(count=30):
    rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: rank = int(f.read().strip())
            except: rank = 0
    
    targets = []
    sources = [
        "https://tranco-list.eu/download/daily/top-1m.csv",
        "https://raw.githubusercontent.com/pytoolz/tranco-list/master/top-1m.csv"
    ]
    
    for url in sources:
        try:
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
        except: continue

    if not targets:
        hardcoded = ["google.com", "apple.com", "microsoft.com", "amazon.com", "netflix.com"]
        targets = [{"domain": d, "rank": rank + i + 1} for i, d in enumerate(hardcoded)]

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
        cat_id = category.lower().replace(" ", "_").strip()
        folder = os.path.join(BASE_PATH, cat_id)
        os.makedirs(folder, exist_ok=True)
        
        file_id = f"{site['domain'].replace('.', '_')}.json"
        intel_record = {
            "meta": {"rank": site['rank'], "site": site['domain'], "date": TIMESTAMP},
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
    targets = get_prime_targets(30)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    for target in targets:
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Return ONLY JSON. Keys: Architecture, Cyber-Defense, UX-Laws, Brand-DNA. List of 5 objects: {title, description, technical_spec, severity_score(1-100)}."},
                    {"role": "user", "content": f"Deconstruct: {target['domain']}"}
                ],
                response_format={"type": "json_object"}
            )
            build_vault(target, json.loads(res.choices[0].message.content))
            print(f"✅ Indexed: {target['domain']}")
        except Exception as e: print(f"❌ Error {target['domain']}: {e}")

if __name__ == "__main__":
    execute_vision()
