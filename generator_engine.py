import os
import sys
import json
import openai

def run():
    target_site = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    print(f"🔍 Starting scan for: {target_site}")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY is missing!")
        return

    client = openai.OpenAI(api_key=api_key)

    try:
      print("⚖️ Formulating New Laws for the Codex...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview", # או gpt-3.5-turbo
            messages=[{
                "role": "system", 
                "content": "You are the Chief Legislator of the Codex Law Engine. Your job is to scan websites and derive universal digital laws from their failures. Return ONLY a JSON object."
            },
            {
                "role": "user", 
                "content": f"Analyze {target_site}. For every security flaw or technical failure found, formulate a formal Digital Law. "
                           f"The output must be a list under the key 'security_flaws'. "
                           f"Each item must have: 'law_id' (e.g., CL-10x), 'flaw' (The law name), 'description' (The formal law text), and 'severity'."
            }]
        )
        
        raw_result = response.choices[0].message.content
        print("✅ OpenAI responded successfully!")
        
        # ניסיון לנקות את התשובה אם ה-AI הוסיף ```json
        clean_result = raw_result.replace('```json', '').replace('```', '').strip()
        ai_data = json.loads(clean_result)

        file_path = 'Market_Analysis/scanned_laws.json'
        
        # קריאת הנתונים הקיימים
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
        else:
            db = {}

        # עדכון ושמירה
        db[target_site] = ai_data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        print(f"💾 Successfully saved data for {target_site}")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    run()
