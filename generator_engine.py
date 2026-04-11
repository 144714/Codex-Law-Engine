import os
import json
from openai import OpenAI

# המנוע שואב את המפתח הסודי מהכספת של גיטהב באופן אוטומטי
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_ai_laws(prompt_from_user):
    # כאן ה-AI מקבל את ההנחיות שלך וממציא חוקים
    response = client.chat.completions.create(
        model="gpt-4", # או gpt-3.5-turbo
     messages=[
    {"role": "system", "content": "You are the Codex Anti-Bot Commander. Generate a list of 10 sophisticated technical laws to detect and block non-human traffic and spam comments."},
    {"role": "user", "content": "The targets are: Automated form fillers, fake comment bots, and scrapers."}
]
        ]
    )
    
    laws = response.choices[0].message.content
    return json.loads(laws)

# הניסוי הראשון: בקשה מבעל אתר
if __name__ == "__main__":
    user_request = "אני רוצה שאף אחד לא יוכל להעתיק תמונות מהאתר שלי"
    new_laws = generate_ai_laws(user_request)
    
    # שמירת החוקים החדשים לקובץ
    with open("generated_laws.json", "w", encoding="utf-8") as f:
        json.dump(new_laws, f, ensure_ascii=False, indent=2)
    
    print("ה-AI יצר חוקים חדשים ושמר אותם בהצלחה!")
