import os, sys, json, openai, hashlib

# קביעת נתיבים אבסולוטיים
BASE_PATH = os.path.join(os.getcwd(), 'Market_Analysis')
INDEX_FILE = os.path.join(BASE_PATH, 'master_index.json')

def setup_environment():
    if not os.path.exists(BASE_PATH):
        os.makedirs(BASE_PATH)

def get_target_sites():
    """מחלץ אתרים מכל מקור אפשרי (Issue או ידני)"""
    if os.getenv("GITHUB_EVENT_NAME") == "issues":
        with open(os.getenv("GITHUB_EVENT_PATH"), 'r') as f:
            event = json.load(f)
            return [s.strip() for s in event['issue']['body'].replace('\n', ',').split(',') if s.strip()]
    return [s.strip() for s in sys.argv[1].split(',') if s and s.strip()] if len(sys.argv) > 1 else []

def save_entry(site, category, data):
    """שומר כל אתר בקובץ נפרד תחת הקטגוריה שלו - מבנה Scalable"""
    cat_dir = os.path.join(BASE_PATH, category.replace(" ", "_"))
    if not os.path.exists(cat_dir): os.makedirs(cat_dir)
    
    file_path = os.path.join(cat_dir, f"{site.replace('.', '_')}.json")
    
    # הוספת מטה-דאטה לכל כניסה
    entry = {
        "site": site,
        "category": category,
        "timestamp": os.popen('date -I').read().strip(),
        "laws": data
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    return file_path

def update_master_index(site, category):
    """מעדכן אינדקס מרכזי כדי שהאתר ידע איפה לחפש כל דבר"""
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as f: index = json.load(f)
    
    if category not in index: index[category] = []
    if site not in index[category]: index[category].append(site)
    
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

def run_pipeline():
    setup_environment()
    sites = get_target_sites()
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    for site in sites:
        print(f"🚀 Processing: {site}")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional auditor. Return a JSON with categories: UI-Design, Security, UX, Accessibility. Each category must have a list of laws with: title, description, design_token, remediation."},
                    {"role": "user", "content": f"Full audit for {site}"}
                ],
                response_format={"type": "json_object"}
            )
            raw_data = json.loads(response.choices[0].message.content)
            
            # הקוד רץ על כל קטגוריה שה-AI החזיר ושומר בנפרד
            for cat, laws in raw_data.items():
                if isinstance(laws, list):
                    save_entry(site, cat, laws)
                    update_master_index(site, cat)
            print(f"✅ {site} ingested successfully.")
        except Exception as e:
            print(f"❌ Failed {site}: {e}")

if __name__ == "__main__":
    run_pipeline()
