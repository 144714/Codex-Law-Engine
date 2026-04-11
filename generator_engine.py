import os
import sys
import json
import openai
import re

def run():
    target_site = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    print(f"⚖️ Extracting Laws from: {target_site}")
    
    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)

    try:
        # ה-Prompt החדש והחזק שלנו
        prompt = (
            f"Analyze the website {target_site}. Identify 3-5 technical or security failures. "
            f"Convert each failure into a formal Law for the 'Codex Law Engine'. "
            f"Format as JSON only with the key 'security_flaws'. Each item must have: "
            f"'law_id' (e.g., CL-101), 'flaw' (Short Law Name), 'description' (Formal Law Text), 'severity'."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # או gpt-4-turbo-preview אם יש לך הרשאות
            messages=[
                {"role": "system", "content": "You are a Digital Legislator. You output ONLY pure JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        raw_result = response.choices[0].message.content
        
        # ניקוי אגרסיבי של התשובה כדי למנוע Exit Code 1
        json_match = re.search(r'\{.*\}', raw_result, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group(0))
        else:
            raise ValueError("AI did not return valid JSON format")

        file_path = 'Market_Analysis/scanned_laws.json'
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            db = {}

        # הוספת האתר למאגר החוקים המצטבר
        db[target_site] = ai_data
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Laws for {target_site} have been codified.")

    except Exception as e:
        print(f"❌ LEGISLATIVE ERROR: {str(e)}")
        sys.exit(1) # מדווח לגיטהב שמשהו נכשל

if __name__ == "__main__":
    run()
