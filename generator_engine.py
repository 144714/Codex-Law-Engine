import os, sys, json, openai, re

# הגדרות נתיבים
BASE_DIR = 'Market_Analysis'
MAIN_FILE = os.path.join(BASE_DIR, 'scanned_laws.json')

def ensure_directories():
    """מבטיח שתיקיית הבסיס קיימת"""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"📁 Created base directory: {BASE_DIR}")

def save_to_category(site_name, laws_data):
    """
    מפצל את החוקים לקבצים נפרדים לפי הקטגוריה.
    מטפל גם במקרים שה-AI מחזיר רשימה [] במקום אובייקט {}.
    """
    # תיקון שגיאת ה-List: אם הנתונים הגיעו כרשימה, נהפוך אותם לדיקשנרי
    if isinstance(laws_data, list):
        laws_data = {f"CL-{i+1:02d}": item for i, item in enumerate(laws_data)}
    
    # וידוא שיש לנו דיקשנרי לעבוד איתו
    if not isinstance(laws_data, dict):
        print(f"⚠️ Warning: Unexpected data format for {site_name}")
        return

    for law_id, details in laws_data.items():
        # הגנה מפני תתי-אלמנטים שאינם דיקשנרי
        if not isinstance(details, dict):
            continue
            
        # חילוץ קטגוריה וניקוי תווים
        category = details.get('category', 'General').strip().replace("/", "-")
        category_path = os.path.join(BASE_DIR, category)
        
        if not os.path.exists(category_path):
            os.makedirs(category_path)
        
        # שם קובץ מבוסס קטגוריה (למשל: ui_design_laws.json)
        file_name = f"{category.lower().replace(' ', '_')}_laws.json"
        full_path = os.path.join(category_path, file_name)
        
        # טעינת נתונים קיימים בקטגוריה (כדי להוסיף עליהם)
        cat_db = {}
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                try:
                    cat_db = json.load(f)
                except:
                    cat_db = {}
        
        # עדכון המידע עבור האתר הספציפי
        if site_name not in cat_db:
            cat_db[site_name] = {}
        
        cat_db[site_name][law_id] = details
        
        # שמירה לקובץ הקטגוריה
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(cat_db, f, indent=2, ensure_ascii=False)

def run_audit():
    # קבלת אתרים מהטרמינל
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    if not target_sites:
        print("❌ Usage: python codex_engine.py 'site1.com, site2.com'")
        return

    ensure_directories()
    
    # שליפת מפתח ה-API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment variables.")
        return
        
    client = openai.OpenAI(api_key=api_key)

    for site in target_sites:
        print(f"\n⚖️  The Codex is analyzing: {site}...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the 'Chief Digital Legislator' for The Codex Analysis. "
                            "Audit websites against global standards. "
                            "Categories MUST be one of: Security, Accessibility, Performance, UI-Design, UX-Flow. "
                            "Return ONLY a JSON object where keys are law IDs (e.g., CL-01). "
                            "Each law must have: 'title', 'status' (Issue/Compliant), 'category', 'description', 'remediation'."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Perform a high-end 2060-style audit on {site}. Be extremely detailed. Identify 15-20 distinct laws (both issues and compliant points)."
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # המרת טקסט ה-JSON לאובייקט פייתון
            raw_content = response.choices[0].message.content
            laws_found = json.loads(raw_content)
            
            # 1. שמירה לפי תיקיות קטגוריה
            save_to_category(site, laws_found)
            
            # 2. שמירה לקובץ הראשי המאוחד (לצורך גיבוי ודאשבורד כללי)
            all_data = {}
            if os.path.exists(MAIN_FILE):
                with open(MAIN_FILE, 'r', encoding='utf-8') as f:
                    try: all_data = json.load(f)
                    except: all_data = {}
            
            all_data[site] = laws_found
            with open(MAIN_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Success! {site} codified and categorized.")
            
        except Exception as e:
            print(f"⚠️ Failed to analyze {site}: {str(e)}")

if __name__ == "__main__":
    run_audit()
