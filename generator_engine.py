import os, sys, json, openai, re

def run():
    input_data = sys.argv[1] if len(sys.argv) > 1 else ""
    target_sites = [s.strip() for s in input_data.split(',') if s.strip()]
    
    if not target_sites:
        print("No sites to process.")
        return

    file_path = 'Market_Analysis/scanned_laws.json'
    db = json.load(open(file_path, 'r', encoding='utf-8')) if os.path.exists(file_path) else {}

    api_key = os.getenv("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)

    for site in target_sites:
        print(f"⚖️ Legislating for: {site}")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Digital Legislator. Formulate 10 formal laws (ID: CL-xxx) based on security flaws. Return ONLY JSON with key 'security_flaws'."},
                    {"role": "user", "content": f"Analyze {site}"}
                ]
            )
            raw = response.choices[0].message.content
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                db[site] = json.loads(match.group(0))
                print(f"✅ Codified {site}")
        except Exception as e:
            print(f"❌ Error with {site}: {e}")

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run()
