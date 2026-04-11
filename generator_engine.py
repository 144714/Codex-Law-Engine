import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# רשימת הקטגוריות של Codex
CATEGORIES = {
    "Spam_Protection": "Detecting bots, fake comments, and form spam.",
    "Data_Privacy": "GDPR compliance, cookie consent, and data encryption rules.",
    "Security": "Preventing SQL injection, XSS attacks, and brute force.",
    "Performance": "Image optimization, caching rules, and server load balancing.",
    "User_Experience": "Accessibility rules, broken link detection, and mobile responsiveness."
}

def generate_laws_for_category(category_name, description):
    print(f"🏗️ מייצר חוקים עבור: {category_name}...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # מהיר וזול לייצור המוני
        messages=[
            {"role": "system", "content": f"You are a legal-tech AI. Generate 50 technical website laws for the category: {category_name}. Use JSON format."},
            {"role": "user", "content": f"Context: {description}"}
        ]
    )
    return json.loads(response.choices[0].message.content)

if __name__ == "__main__":
    for cat_name, cat_desc in CATEGORIES.items():
        laws = generate_laws_for_category(cat_name, cat_desc)
        
        # יצירת תיקייה לכל קטגוריה אם היא לא קיימת
        if not os.path.exists(cat_name):
            os.makedirs(cat_name)
            
        file_path = os.path.join(cat_name, "laws.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(laws, f, ensure_ascii=False, indent=2)

    print("🚀 המשימה הושלמה! כל החוקים קוטלגו בתיקיות.")
