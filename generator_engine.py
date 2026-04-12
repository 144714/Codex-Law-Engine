import os, sys, json, openai, re

# הגדרות נתיבים
BASE_DIR = 'Market_Analysis'
MAIN_FILE = os.path.join(BASE_DIR, 'scanned_laws.json')

def ensure_directories():
    """יוצר את תיקיית הבסיס אם היא לא קיימת"""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"📁 Created base directory: {BASE_DIR}")

def save_to_category(site_name, laws_data):
    """מפצל את החוקים לקבצים נפרדים לפי הקטגוריה שלהם"""
    for law_id, details in laws_data.items():
        # חילוץ קטגוריה וניקוי תווים בעייתיים
        category = details.get('category', 'General').strip().replace("/", "-")
        category_path = os.path.join(BASE_DIR, category)
        
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        file_name = f"{category.lower().replace(' ', '_')}_laws.json"
        full_path = os.path.join(category_path, file_name)
        
        # טעינת מידע קיים בקטגוריה כדי לא לדרוס
        cat_db = {}
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                try: cat_db = json.load(f)
                except: cat_db = {}
        
        # עדכון המידע
        if site_name not in cat_db: cat_db[site_name] = {}
        cat_db[site_name][law_id] = details
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(cat_db, f, indent=2, ensure_ascii=False)

def run_audit():
    # קבלת אתרים מהמשתמש
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    if not target_sites:
        print("❌ No sites provided. Usage: python script.py 'site1.com, site2.com'")
        return

    ensure_directories()
    
    # הגדרת הלקוח
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in target_sites:
        print(f"\n⚖️  The Codex is analyzing: {site}...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the 'Chief Digital Legislator'. Audit sites against 'The Codex'. "
                            "Categories: Security, Accessibility, Performance, UI-Design, UX-Flow. "
                            "Return ONLY a JSON object. Each law must have: "
                            "'title', 'status' (Issue/Compliant), 'category', 'description', 'remediation'."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Perform a 2060-style audit on {site}. Be extremely detailed. Return 15-20 laws."
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # פענוח התוצאה
            laws_found = json.loads(response.choices[0].message.content)
            
            # שמירה לפי קטגוריות
            save_to_category(site, laws_found)
            
            # שמירה גם לקובץ הראשי המאוחד
            all_data = {}
            if os.path.exists(MAIN_FILE):
                with open(MAIN_FILE, 'r', encoding='utf-8') as f:
                    try: all_data = json.load(f)
                    except: all_data = {}
            
            all_data[site] = laws_found
            with open(MAIN_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Finished {site}. Data categorized in folders.")
            
        except Exception as e:
            print(f"⚠️ Error analyzing {site}: {e}")

if __name__ == "__main__":
    run_audit()
