import os, json, openai, urllib.request, datetime, hashlib, time

# --- CONFIGURATION ---
BASE_PATH = 'Codex_Intelligence'
OUTPUT_PATH = 'Generated_Sites'
INDEX_FILE = os.path.join(BASE_PATH, 'global_registry.json')
STATE_FILE = 'engine_state.log'
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def setup_env():
    for path in [BASE_PATH, OUTPUT_PATH]:
        if not os.path.exists(path): os.makedirs(path)

def get_prime_targets(count=15):
    rank = 0
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            try: rank = int(f.read().strip())
            except: rank = 0
    
    targets = []
    url = "https://tranco-list.eu/download/daily/top-1m.csv"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            for i, line in enumerate(resp):
                if i < rank: continue
                decoded = line.decode('utf-8').strip()
                if ',' in decoded:
                    targets.append({"domain": decoded.split(',')[1], "rank": i + 1})
                if len(targets) >= count: break
    except:
        targets = [{"domain": "apple.com", "rank": 1}, {"domain": "stripe.com", "rank": 2}]
    
    with open(STATE_FILE, 'w') as f: f.write(str(rank + len(targets)))
    return targets

def build_vault(site, audit):
    master_index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r', encoding='utf-8') as f: master_index = json.load(f)

    for category, laws in audit.items():
        cat_id = category.upper().replace(" ", "_")
        cat_dir = os.path.join(BASE_PATH, cat_id)
        os.makedirs(cat_dir, exist_ok=True)
        
        file_path = os.path.join(cat_dir, f"{site['domain'].replace('.', '_')}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({"meta": site, "data": laws, "scanned": TIMESTAMP}, f, indent=2)
        
        if cat_id not in master_index: master_index[cat_id] = []
        if site['domain'] not in master_index[cat_id]: master_index[cat_id].insert(0, site['domain'])

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_index, f, indent=2)

def generate_ultimate_startup():
    """האדריכל: יוצר אתר מהדאטה שנאסף בסבב הנוכחי"""
    print("🏗️  Architect: Forging Ultimate Startup Site...")
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # שליפת דאטה לדוגמה מהסריקה האחרונה
    prompt = "Build a luxury SaaS Landing Page using Tailwind CSS. Use Glassmorphism, Dark Mode, and high-end typography. Focus on extreme UI/UX standards found in top 1% global sites."
    
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are the Codex Architect."}, {"role": "user", "content": prompt}]
    )
    
    with open(os.path.join(OUTPUT_PATH, 'latest_dna_site.html'), 'w', encoding='utf-8') as f:
        f.write(res.choices[0].message.content.replace("```html", "").replace("```", ""))

def run():
    setup_env()
    targets = get_prime_targets()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    for target in targets:
        print(f"📡 Auditing: {target['domain']}")
        try:
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "Return ONLY JSON. 6 Categories: VISUAL_ENGINEERING, SECURITY, UX_FLOW, PERFORMANCE, ARCHITECTURE, CONVERSION. 6 laws per category: {title, description, technical_spec, severity_score}."},
                          {"role": "user", "content": f"Audit: {target['domain']}"}],
                response_format={"type": "json_object"}
            )
            build_vault(target, json.loads(res.choices[0].message.content))
        except: continue
    
    generate_ultimate_startup()

if __name__ == "__main__":
    run()
