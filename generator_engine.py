import os, sys, json, openai, hashlib

# --- הגדרות בסיס ---
BASE_DIR = 'Market_Analysis'
REGISTRY_FILE = os.path.join(BASE_DIR, 'global_laws_registry.json')

def get_input_sites():
    """מחלץ את האתרים בין אם זה ידני ובין אם זה מ-Issue"""
    event_name = os.getenv("GITHUB_EVENT_NAME")
    
    # אם הופעל דרך פתיחת Issue באתר
    if event_name == "issues":
        event_path = os.getenv("GITHUB_EVENT_PATH")
        with open(event_path, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
            # לוקח את תוכן ה-Issue (ה-Body) שבו כתבת את האתרים
            issue_body = event_data.get('issue', {}).get('body', '')
            return [s.strip() for s in issue_body.replace('\n', ',').split(',') if s.strip()]
    
    # אם הופעל ידנית דרך ה-Actions
    elif len(sys.argv) > 1 and sys.argv[1]:
        return [s.strip() for s in sys.argv[1].split(',') if s.strip()]
    
    return []

def save_to_category(site_name, laws_data, registry):
    if not isinstance(laws_data, dict): return 0
    added_count = 0

    for _, details in laws_data.items():
        if not isinstance(details, dict): continue
        
        title = details.get('title', 'Unknown Concept')
        law_hash = hashlib.md5(title.lower().encode()).hexdigest()
        final_id = f"DNA-{law_hash[:6].upper()}"
        
        # בחירת תיקייה לפי הקטגוריה שה-AI קבע
        category = details.get('category', 'General').strip().replace(" ", "-")
        category_dir = os.path.join(BASE_DIR, category)
        if not os.path.exists(category_dir): os.makedirs(category_dir)
        
        file_path = os.path.join(category_dir, f"{category.lower()}_vault.json")
        
        # טעינה ועדכון הכספת הקטגוריאלית
        db = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try: db = json.load(f)
                except: db = {}
        
        if site_name not in db: db[site_name] = {}
        db[site_name][final_id] = {
            "title": title,
            "description": details.get('description', ''),
            "design_token": details.get('design_token', 'N/A'),
            "remediation": details.get('remediation', ''),
            "category": category,
            "status": details.get('status', 'Analyzed')
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        added_count += 1
    return added_count

def run_audit():
    sites = get_input_sites()
    if not sites:
        print("❌ No sites found to scan.")
        return

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in sites:
        print(f"🧬 Scanning DNA for: {site}...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Design & Security Auditor. Return ONLY a JSON object with laws and design_tokens. Categories: UI-Design, Security, UX-Flow, Accessibility."},
                    {"role": "user", "content": f"Audit {site} and extract 10 technical design and security laws."}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            # אם ה-AI מחזיר רשימה תחת מפתח מסוים, נחלץ אותה
            laws = data.get('laws', data) 
            save_to_category(site, laws, {})
            print(f"✅ Finished {site}")
        except Exception as e:
            print(f"⚠️ Error scanning {site}: {e}")

if __name__ == "__main__":
    run_audit()
