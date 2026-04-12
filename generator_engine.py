import os, sys, json, openai, hashlib

BASE_DIR = 'Market_Analysis'
REGISTRY_FILE = os.path.join(BASE_DIR, 'global_laws_registry.json')

def get_law_hash(title):
    """יוצר מזהה ייחודי לכל חוק לפי השם שלו כדי למנוע כפילויות"""
    return hashlib.md5(title.strip().lower().encode()).hexdigest()

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_registry(registry):
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def save_to_category(site_name, laws_data, registry):
    if isinstance(laws_data, list):
        laws_data = {f"CL-{get_law_hash(item.get('title', '')):5}": item for item in laws_data}
    
    new_laws_found = 0

    for law_id, details in laws_data.items():
        title = details.get('title', '')
        law_hash = get_law_hash(title)
        
        # --- המנגנון החכם: בדיקה אם החוק כבר קיים במאגר הגלובלי ---
        if law_hash in registry and site_name in registry[law_hash].get('sites', []):
            continue # מדלג - כבר סרקנו את האתר הזה לחוק הזה
        
        category = details.get('category', 'General').strip().replace("/", "-")
        category_path = os.path.join(BASE_DIR, category)
        if not os.path.exists(category_path): os.makedirs(category_path)
        
        file_name = f"{category.lower().replace(' ', '_')}_laws.json"
        full_path = os.path.join(category_path, file_name)
        
        # עדכון הקובץ הקטגוריאלי
        cat_db = {}
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                try: cat_db = json.load(f)
                except: cat_db = {}
        
        if site_name not in cat_db: cat_db[site_name] = {}
        cat_db[site_name][law_id] = details
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(cat_db, f, indent=2, ensure_ascii=False)
        
        # עדכון הרג'יסטרי הגלובלי
        if law_hash not in registry:
            registry[law_hash] = {"title": title, "category": category, "sites": []}
        if site_name not in registry[law_hash]["sites"]:
            registry[law_hash]["sites"].append(site_name)
        
        new_laws_found += 1
    
    return new_laws_found

def run_audit():
    # תמיכה באלפי אתרים מתוך קובץ או רשימה
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    registry = load_registry()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in target_sites:
        # בדיקה אם האתר כבר נסרק לעומק (אופציונלי)
        print(f"🚀 Processing: {site}")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a bulk auditor. Return JSON ONLY. Categories: Security, Accessibility, Performance, UI-Design, UX-Flow."},
                    {"role": "user", "content": f"Audit {site}. List 15 laws. If a law is standard, use its common industry name."}
                ],
                response_format={"type": "json_object"}
            )
            
            laws = json.loads(response.choices[0].message.content)
            added = save_to_category(site, laws, registry)
            print(f"✅ {site}: Added {added} new unique records.")
            
        except Exception as e:
            print(f"⚠️ Error with {site}: {e}")

    save_registry(registry)

if __name__ == "__main__":
    run_audit()
