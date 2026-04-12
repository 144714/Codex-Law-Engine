import os, sys, json, openai, hashlib

# הגדרות נתיבים
BASE_DIR = 'Market_Analysis'
REGISTRY_FILE = os.path.join(BASE_DIR, 'global_laws_registry.json')

def get_law_hash(title):
    """יוצר מזהה ייחודי לכל חוק/ערך עיצובי למניעת כפילויות"""
    return hashlib.md5(title.strip().lower().encode()).hexdigest()

def load_registry():
    """טוען את המוח המרכזי של המערכת"""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_registry(registry):
    """שומר את המאגר המעודכן"""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def save_to_category(site_name, laws_data, registry):
    """מקטלג חוקים ומחלץ Design Tokens ליצירה עתידית"""
    
    # טיפול בפורמטים שונים של תגובת AI
    if isinstance(laws_data, list):
        laws_data = {f"temp_{i}": item for i, item in enumerate(laws_data)}
    
    if not isinstance(laws_data, dict):
        return 0

    new_records_found = 0

    for _, details in laws_data.items():
        if not isinstance(details, dict): continue
            
        title = details.get('title', 'Unknown Concept')
        law_hash = get_law_hash(title)
        final_id = f"CODE-{law_hash[:6].upper()}"
        
        # בדיקה אם הערך כבר קיים לאתר הזה
        if law_hash in registry and site_name in registry[law_hash].get('sites', []):
            continue 
        
        # בחירת קטגוריה - הגבלה לקטגוריות עיצוב ומבנה
        category = details.get('category', 'Design-System').strip().replace("/", "-")
        category_path = os.path.join(BASE_DIR, category)
        if not os.path.exists(category_path): os.makedirs(category_path)
        
        file_name = f"{category.lower().replace(' ', '_')}_vault.json"
        full_path = os.path.join(category_path, file_name)
        
        # עדכון בסיס הנתונים הקטגוריאלי
        cat_db = {}
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                try: cat_db = json.load(f)
                except: cat_db = {}
        
        if site_name not in cat_db: cat_db[site_name] = {}
        
        # הוספת שדה ה-Token אם קיים (זה המפתח ליצירה בעתיד)
        cat_db[site_name][final_id] = {
            "title": title,
            "description": details.get('description', ''),
            "design_token": details.get('design_token', 'N/A'), # הערך הטכני (למשל #FFFFFF)
            "remediation": details.get('remediation', ''),
            "category": category
        }
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(cat_db, f, indent=2, ensure_ascii=False)
        
        # עדכון הרג'יסטרי הגלובלי
        if law_hash not in registry:
            registry[law_hash] = {"title": title, "category": category, "sites": []}
        if site_name not in registry[law_hash]["sites"]:
            registry[law_hash]["sites"].append(site_name)
        
        new_records_found += 1
    
    return new_records_found

def run_audit():
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    if not target_sites: return

    registry = load_registry()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in target_sites:
        print(f"🏗️  Extracting Design DNA from: {site}")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o", # מומלץ להשתמש ב-4o לדיוק בעיצוב, או 3.5-turbo לחיסכון
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are a Senior Design Systems Engineer. Extract the 'DNA' of a website. "
                            "Focus on: Typography, Color-System, Spacing, Component-Style, and UX-Logic. "
                            "For every item, you MUST provide a 'design_token' field with a technical CSS-like value. "
                            "Example: { 'title': 'Primary Button Radius', 'design_token': 'border-radius: 12px', 'category': 'UI-Design' }. "
                            "Return ONLY a JSON object."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Analyze {site}. Return 15 laws/tokens that define its unique design system."
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            laws_found = json.loads(response.choices[0].message.content)
            added = save_to_category(site, laws_found, registry)
            print(f"✨ {site}: Ingested {added} design tokens.")
            
        except Exception as e:
            print(f"⚠️ Error with {site}: {e}")

    save_registry(registry)
    print("\n✅ Machine Learning Dataset Updated.")

if __name__ == "__main__":
    run_audit()
