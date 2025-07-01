import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

EXAMPLES_DIR = Path('examples')
OUTPUTS_DIR = Path('outputs')
OUTPUT_FILE = OUTPUTS_DIR / 'notes.json'


def list_json_files(directory: Path):
    return [f for f in directory.glob('*.json') if f.is_file()]


def select_file(files):
    print("\nAvailable files:")
    for idx, file in enumerate(files, 1):
        print(f"{idx}. {file.name}")
    while True:
        try:
            choice = int(input(f"Select a file to process (1-{len(files)}): "))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def load_messages(file_path: Path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('messages', [])


def process_message_with_openai(msg, client):
    # Russian Zettelkasten prompt with ID, date, and text
    escaped_text = msg.get('text', '').replace('"', '\"')
    prompt = f"""
Преврати следующий пост из Telegram в Zettelkasten-заметку, только если он информативный (то есть содержит идею, действие или факт). Если он слишком короткий, водянистый или бессмысленный — верни просто `SKIP`.

Используй формат вывода:

---
## Zettel: {{{{гггг-мм-дд}}}}-{{{{id}}}}
### Название: {{{{1–2 слова, отражающие суть}}}}
**Теги**: #тег1 #тег2  
**Дата**: {{{{дата поста}}}}  
**Источник**: ID {{{{id}}}}

{{{{Краткое содержание на 1–3 предложения. Без воды.}}}}
---

Пост:
ID: {msg.get('id')}
Дата: {msg.get('date')}
Текст: "{escaped_text}"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI error: {e}]"


def main():
    files = list_json_files(EXAMPLES_DIR)
    if not files:
        print("No JSON files found in examples folder.")
        return
    selected_file = select_file(files)
    print(f"\nProcessing file: {selected_file.name}")
    messages = load_messages(selected_file)
    if not messages:
        print("No messages found in the selected file.")
        return
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("OPENAI_API_KEY not set in environment.")
        return
    client = OpenAI(api_key=openai_api_key)
    print(f"\nProcessing {len(messages)} messages through OpenAI GPT-4o...")
    processed = []
    for idx, msg in enumerate(messages, 1):
        text = msg.get('text', '')
        if not text:
            continue
        summary = process_message_with_openai(msg, client)
        processed.append({
            'id': msg.get('id'),
            'summary': summary
        })
        print(f"[{idx}/{len(messages)}] Done")
    # Ensure output directory exists
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    # Create output file name based on input file
    input_stem = selected_file.stem.replace('raw_dump_', '')
    output_file = OUTPUTS_DIR / f'notes_{input_stem}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2, ensure_ascii=False)
    print(f"\nAll summaries saved to {output_file}")

if __name__ == "__main__":
    main() 