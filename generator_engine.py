import os, sys, json, openai, hashlib

# הגדרות נתיבים
BASE_DIR = 'Market_Analysis'
REGISTRY_FILE = os.path.join(BASE_DIR, 'global_laws_registry.json')

def get_law_hash(title):
    """יוצר מזהה ייחודי לכל חוק לפי השם שלו למניעת כפילויות"""
    return hashlib.md5(title.strip().lower().encode()).hexdigest()

def load_registry():
    """טוען את מאגר החוקים הקיים"""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_registry(registry):
    """שומר את מאגר החוקים המעודכן"""
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def save_to_category(site_name, laws_data, registry):
    """מפצל את החוקים לקטגוריות ומנהל רישום גלובלי"""
    
    # תיקון השגיאה הקודמת: טיפול במקרה שה-AI מחזיר רשימה [] במקום דיקשנרי {}
    if isinstance(laws_data, list):
        laws_data = {f"temp_{i}": item for i, item in enumerate(laws_data)}
    
    if not isinstance(laws_data, dict):
        print(f"⚠️ Warning: Invalid data format for {site_name}")
        return 0

    new_laws_found = 0

    for _, details in laws_data.items():
        if not isinstance(details, dict):
            continue
            
        title = details.get('title', 'Unknown Law')
        law_hash = get_law_hash(title)
        
        # יצירת מזהה חוק קבוע (CL-XXXXXX) מבוסס על התוכן שלו
        final_law_id = f"CL-{law_hash[:6].upper()}"
        
        # מניעת כפילות: אם האתר כבר נסרק לחוק הספציפי הזה - דלג
        if law_hash in registry and site_name in registry[law_hash].get('sites', []):
            continue 
        
        # ניקוי שם הקטגוריה ויצירת תיקייה
        category = details.get('category', 'General').strip().replace("/", "-")
        category_path = os.path.join(BASE_DIR, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        file_name = f"{category.lower().replace(' ', '_')}_laws.json"
        full_path = os.path.join(category_path, file_name)
        
        # טעינת נתונים קיימים בקטגוריה
        cat_db = {}
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                try: cat_db = json.load(f)
                except: cat_db = {}
        
        # הוספת החוק תחת האתר המתאים
        if site_name not in cat_db:
            cat_db[site_name] = {}
        cat_db[site_name][final_law_id] = details
        
        # שמירה לקובץ הקטגוריאלי
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(cat_db, f, indent=2, ensure_ascii=False)
        
        # עדכון הרג'יסטרי המרכזי
        if law_hash not in registry:
            registry[law_hash] = {"title": title, "category": category, "sites": []}
        if site_name not in registry[law_hash]["sites"]:
            registry[law_hash]["sites"].append(site_name)
        
        new_laws_found += 1
    
    return new_laws_found

def run_audit():
    # קבלת האתרים מה-Input (מופרדים בפסיקים)
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    if not target_sites:
        print("❌ Error: No sites provided.")
        return

    # טעינת המוח המרכזי
    registry = load_registry()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: API Key missing.")
        return
        
    client = openai.OpenAI(api_key=api_key)

    for site in target_sites:
        print(f"🚀 Codex Engine is auditing: {site}")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are a bulk digital auditor. Return ONLY a JSON object. "
                            "Categories: Security, Accessibility, Performance, UI-Design, UX-Flow. "
                            "For each item provide: title, status (Issue/Compliant), category, description, remediation."
                        )
                    },
                    {
                        "role": "user", 
                        "content": f"Audit {site} and list 15 digital laws. Be precise."
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            laws_found = json.loads(raw_content)
            
            added = save_to_category(site, laws_found, registry)
            print(f"✅ {site}: {added} new unique laws codified.")
            
        except Exception as e:
            print(f"⚠️ Error processing {site}: {str(e)}")

    # שמירת המוח המרכזי לאחר כל הסריקות
    save_registry(registry)
    print("\n🏁 Bulk Audit Complete. All data synchronized to Market_Analysis/")

if __name__ == "__main__":
    run_audit()
