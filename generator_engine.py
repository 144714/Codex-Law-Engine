# זהו המנוע של קודקס - Codex Engine v1.0
import json

class CodexGenerator:
    def __init__(self):
        self.laws = []

    def add_law(self, id, name, condition, action):
        # פונקציה שמוסיפה חוק חדש לרשימה
        new_law = {
            "id": id,
            "name": name,
            "condition": condition,
            "action": action
        }
        self.laws.append(new_law)
        print(f"חוק חדש נוצר: {name}")

    def save_laws(self, filename="generated_laws.json"):
        # שומר את כל החוקים לקובץ שגיטהב יכול לקרוא
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.laws, f, ensure_ascii=False, indent=2)
        print(f"כל החוקים נשמרו ב-{filename}")

# הרצה לדוגמה של המנוע
if __name__ == "__main__":
    engine = CodexGenerator()
    # כאן המכונה מוסיפה חוק באופן אוטומטי
    engine.add_law("LAW_004", "חוק מניעת פרסומות קופצות", "popup_count > 0", "block_all_popups")
    engine.save_laws()
