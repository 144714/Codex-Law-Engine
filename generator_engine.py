import os
import json
from openai import OpenAI
import re

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CATEGORIES = {
    "Spam_Protection": "Detecting bots, fake comments, and form spam.",
    "Data_Privacy": "GDPR compliance, cookie consent, and data encryption rules.",
    "Security": "Preventing SQL injection, XSS attacks, and brute force.",
    "Performance": "Image optimization, caching rules, and server load balancing.",
    "User_Experience": "Accessibility rules, broken link detection, and mobile responsiveness."
}

def clean_json_string(text):
    # פונקציה שמחלצת רק את ה-JSON מתוך הטקסט של ה-AI
    match = re.search(r'\[.*\]|\{.*\}', text, re.DOTALL)
    return match.group(0) if match else text

def generate_laws_for_category(category_name, description):
    print(f"🏗️ מייצר חוקים עבור: {category_name}...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a technical API. Return ONLY a valid JSON list of 10 laws. No intro, no outro."},
                {"role": "user", "content": f"Category: {category_name}. Context: {description}"}
            ]
        )
        
        raw_content = response.choices[0].message.content
        clean_content = clean_json_string(raw_content)
        return json.loads(clean_content)
    except Exception as e:
        print(f"⚠️ שגיאה בייצור {category_name}: {e}")
        return []

if __name__ == "__main__":
    for cat_name, cat_desc in CATEGORIES.items():
        laws = generate_laws_for_category(cat_name, cat_desc)
        
        if laws:
            if not os.path.exists(cat_name):
                os.makedirs(cat_name)
                
            file_path = os.path.join(cat_name, "laws.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(laws, f, ensure_ascii=False, indent=2)
            print(f"✅ {cat_name} נשמר בהצלחה.")
