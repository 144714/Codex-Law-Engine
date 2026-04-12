import os, sys, json, openai, re

def run():
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    if not target_sites:
        print("No sites to process.")
        return

    file_path = 'Market_Analysis/scanned_laws.json'
    
    # טעינת בסיס הנתונים הקיים
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    else:
        db = {}

    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)

    for site in target_sites:
        print(f"⚖️ Analyzing System: {site}")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # או gpt-4 אם אתה רוצה דיוק מקסימלי
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are the Chief Digital Auditor for 'The Codex Analysis'. "
                            "Your task is to audit websites based on global standards (Security, Accessibility, Performance). "
                            "For each site, you must provide a list of 'Laws'. "
                            "CRITICAL: You must include BOTH 'Issues' (flaws) and 'Compliant' (what the site does well). "
                            "Return ONLY a valid JSON object where keys are law IDs (CL-xxx)."
                        )
                    },
                    {
                        "role": "user", 
                        "content": (
                            f"Analyze {site} in extreme detail. For each law identified, provide: "
                            "1. 'title', 2. 'status' (either 'Issue' or 'Compliant'), "
                            "3. 'category', 4. 'description', 5. 'impact_score' (1-10), "
                            "6. 'remediation' (how to fix or maintain). "
                            "Aim for at least 15-20 laws covering both positives and negatives."
                        )
                    }
                ],
                response_format={ "type": "json_object" } # מבטיח שהפלט יהיה JSON תקין
            )
            
            raw = response.choices[0].message.content
            # פענוח ה-JSON ושמירתו תחת שם האתר
            db[site] = json.loads(raw)
            print(f"✅ Codified {site} with both positive and negative laws.")
            
        except Exception as e:
            print(f"❌ Error with {site}: {e}")

    # שמירה חזרה לקובץ
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    print(f"\n🚀 Analysis complete. Database updated at: {file_path}")

if __name__ == "__main__":
    run()
