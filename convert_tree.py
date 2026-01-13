import re
import json
import os

input_filename = 'tree_tts.txt'
output_filename = 'audio_data.js'

data_structure = {}

# Das bewährte Suchmuster (findet C1_1, D1_1 etc.)
pattern = re.compile(r'([A-Z]\d+_\d+)-(.+)_(\d+)\.m4a')

def get_clean_chapter_name(raw_chap):
    return raw_chap.replace('_', '.')

try:
    # Datei einlesen
    with open(input_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        line = line.strip()
        match = pattern.search(line)
        if match:
            raw_chapter = match.group(1) # z.B. C1_1
            table = match.group(2)       # z.B. 2a
            index = match.group(3)       # z.B. 1
            filename = match.group(0)    # ganzer Dateiname
            
            chapter_name = get_clean_chapter_name(raw_chapter) # C1.1
            
            # Struktur sicherstellen
            if chapter_name not in data_structure:
                data_structure[chapter_name] = {}
            
            if table not in data_structure[chapter_name]:
                data_structure[chapter_name][table] = []
            
            # Sauberen Eintrag hinzufügen (OHNE Title/Artist Tags)
            data_structure[chapter_name][table].append({
                'index': int(index),
                'file': filename,
                'path': f"{chapter_name}/{filename}"
            })
            count += 1

    # Sortieren: Erst Kapitel, dann Tabellen, dann Index
    for chap in data_structure:
        for tab in data_structure[chap]:
            data_structure[chap][tab].sort(key=lambda x: x['index'])

    # JS Datei schreiben
    js_content = f"const audioData = {json.dumps(data_structure, indent=4)};"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"✅ ERFOLG! {count} Dateien verarbeitet.")
    print(f"Die Datei '{output_filename}' wurde neu und sauber erstellt.")

except FileNotFoundError:
    print(f"❌ FEHLER: Die Datei '{input_filename}' wurde nicht gefunden.")
