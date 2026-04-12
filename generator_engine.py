import os, sys, json, openai, hashlib

# הגדרות בסיס - נתיב מוחלט כדי למנוע בעיות בגיטהאב
ROOT_DIR = os.getcwd()
BASE_DIR = os.path.join(ROOT_DIR, 'Market_Analysis')

def get_input_sites():
    event_name = os.getenv("GITHUB_EVENT_NAME")
    if event_name == "issues":
        event_path = os.getenv("GITHUB_EVENT_PATH")
        with open(event_path, 'r', encoding='utf-8') as f:
            event_data = json.load(f)
            issue_body = event_data.get('issue', {}).get('body', '')
            return [s.strip() for s in issue_body.replace('\n', ',').split(',') if s.strip()]
    elif len(sys.argv) > 1 and sys.argv[1]:
        return [s.strip() for s in sys.argv[1].split(',') if s.strip()]
    return []

def save_to_vault(site_name, laws_data):
    if not isinstance(laws_data, dict): return
    
    # אם ה-AI עטף את התשובה במפתח 'laws'
    items = laws_data.get('laws', laws_data)
    if isinstance(items, list):
        items = {f"DNA_{i}": val for i, val in enumerate(items)}

    for _, details in items.items():
        if not isinstance(details, dict): continue
        
        # חילוץ קטגוריה ליצירת תיקייה
        category = details.get('category', 'General').strip().replace(" ", "-")
        category_dir = os.path.join(BASE_DIR, category)
        
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            print(f"📁 Created folder: {category}")
            
        file_path = os.path.join(category_dir, f"{category.lower()}_vault.json")
        
        # טעינת נתונים קיימים
        db = {}
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try: db = json.load(f)
                except: db = {}
        
        # יצירת מזהה ייחודי לחוק
        law_id = f"DNA-{hashlib.md5(details.get('title','').encode()).hexdigest()[:6].upper()}"
        
        if site_name not in db: db[site_name] = {}
        
        db[site_name][law_id] = {
            "title": details.get('title', 'Unknown'),
            "description": details.get('description', ''),
            "design_token": details.get('design_token', 'N/A'),
            "remediation": details.get('remediation', ''),
            "category": category,
            "status": details.get('status', 'Analyzed')
        }
        
        # שמירה פיזית לדיסק
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

def run_audit():
    sites = get_input_sites()
    if not sites: return print("❌ No sites provided.")
    
    if not os.path.exists(BASE_DIR): os.makedirs(BASE_DIR)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in sites:
        print(f"🧬 Scanning DNA for: {site}...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Senior Design & Security Auditor. Return ONLY a JSON object with 'laws'. Categories: UI-Design, Security, UX-Flow, Accessibility. Include 'design_token' for UI items."},
                    {"role": "user", "content": f"Analyze the site {site}. Extract 10 granular design/security laws/tokens."}
                ],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            save_to_vault(site, data)
            print(f"✅ Data saved for {site}")
        except Exception as e:
            print(f"⚠️ Error with {site}: {e}")

if __name__ == "__main__":
    run_audit()
