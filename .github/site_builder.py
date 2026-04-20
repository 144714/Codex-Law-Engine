import os, json, openai

# נתיבי המערכת של Codex
BASE_PATH = 'Codex_Intelligence'
OUTPUT_PATH = 'Generated_Sites'

def get_top_laws(category, limit=12):
    """שואב את חוקי ה-DNA החזקים ביותר מהמאגר שלך"""
    cat_path = os.path.join(BASE_PATH, category.upper())
    
    if not os.path.exists(cat_path):
        print(f"❌ קטגוריה {category} לא נמצאה במאגר.")
        return None

    all_laws = []
    # סריקת הקבצים שנוצרו על ידי ה-Generator
    for file in os.listdir(cat_path):
        if file.endswith('.json'):
            try:
                with open(os.path.join(cat_path, file), 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    # מוסיף את שם האתר לכל חוק כדי שה-AI ידע ממי ללמוד
                    for law in content['data']:
                        law['source_site'] = content['meta']['site']
                        all_laws.append(law)
            except Exception as e:
                continue
    
    # מיון החוקים לפי ציון השפעה (Severity Score) - לוקחים רק את הטובים ביותר
    all_laws.sort(key=lambda x: x.get('severity_score', 0), reverse=True)
    return all_laws[:limit]

def build_startup_from_dna(theme_category):
    """מייצר אתר של מיליארד דולר על בסיס הנתונים שנאספו"""
    laws = get_top_laws(theme_category)
    
    if not laws:
        return

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(f"🏗️  Architect is drafting a site based on {theme_category} Intelligence...")

    prompt = f"""
    You are an Elite Web Developer. Build a complete, high-end Landing Page based on these Technical DNA Laws:
    
    LAWS FROM GLOBAL LEADERS:
    {json.dumps(laws, indent=4)}
    
    INSTRUCTIONS:
    1. Use Tailwind CSS for luxury styling.
    2. Implement EVERY law mentioned in the data.
    3. The site should look like a world-class SaaS startup.
    4. Include a Header, Hero Section with glassmorphism, Features grid, and a dark-mode Footer.
    
    Return ONLY the full HTML code.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You convert raw data DNA into billion-dollar website code."},
                {"role": "user", "content": prompt}
            ]
        )

        code = response.choices[0].message.content
        # ניקוי סימני Markdown אם ה-AI הוסיף
        clean_code = code.replace("```html", "").replace("```", "").strip()

        file_name = f"site_dna_{theme_category.lower()}.html"
        full_output_path = os.path.join(OUTPUT_PATH, file_name)
        
        with open(full_output_path, 'w', encoding='utf-8') as f:
            f.write(clean_code)
        
        print(f"🚀 SUCCESS! Your new site is ready at: {full_output_path}")
        
    except Exception as e:
        print(f"❌ Error building site: {e}")

if __name__ == "__main__":
    # אנחנו בונים אתר שמבוסס על ה-DNA העיצובי והארכיטקטוני הכי חזק שמצאנו
    # ניתן לשנות ל: SECURITY_PROTOCOLS, VISUAL_ENGINEERING וכו'
    build_startup_from_dna("VISUAL_ENGINEERING")
