import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def analyze_site_and_generate_law(url):
    print(f"🔍 סורק אתר: {url}...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a web vulnerability scanner. Identify 5 potential technical flaws for the given URL and generate a fix-law in JSON format."},
                {"role": "user", "content": f"Analyze this site: {url}"}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except:
        return []

if __name__ == "__main__":
    # קריאת רשימת האתרים
    with open("target_sites.txt", "r") as f:
        sites = f.read().splitlines()

    all_scanned_laws = {}

    for site in sites:
        laws = analyze_site_and_generate_law(site)
        all_scanned_laws[site] = laws
        
    # שמירה לתיקייה חדשה של "ניתוח שוק"
    if not os.path.exists("Market_Analysis"):
        os.makedirs("Market_Analysis")
        
    with open("Market_Analysis/scanned_laws.json", "w", encoding="utf-8") as f:
        json.dump(all_scanned_laws, f, ensure_ascii=False, indent=2)

    print("🎯 הסריקה הושלמה! כל הבעיות והפתרונות תועדו.")
