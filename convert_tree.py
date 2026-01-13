import re
import json

input_filename = 'tree_tts.txt'
output_filename = 'audio_data.js'

data_structure = {}

# KORRIGIERTES Regex
# ([A-Z]\d+_\d+) -> Erlaubt C1_1, D1_1, E1_1 etc. (Jeder Großbuchstabe am Anfang)
# -              -> Trennstrich
# (.+)           -> Tabellen-Name (bis zum letzten Unterstrich)
# _              -> Trenner
# (\d+)          -> Index
pattern = re.compile(r'([A-Z]\d+_\d+)-(.+)_(\d+)\.m4a')

def get_clean_chapter_name(raw_chap):
    # Macht aus "C1_1" -> "C1.1" und "D1_1" -> "D1.1"
    return raw_chap.replace('_', '.')

try:
    with open(input_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        line = line.strip()
        match = pattern.search(line)
        if match:
            raw_chapter = match.group(1) # z.B. D1_1
            table = match.group(2)       # z.B. 10a
            index = match.group(3)       # z.B. 1
            filename = match.group(0)
            
            chapter_name = get_clean_chapter_name(raw_chapter) # D1.1
            
            if chapter_name not in data_structure:
                data_structure[chapter_name] = {}
            
            if table not in data_structure[chapter_name]:
                data_structure[chapter_name][table] = []
            
            data_structure[chapter_name][table].append({
                'index': int(index),
                'file': filename,
                'path': f"{chapter_name}/{filename}"
            })
            count += 1

    # Sortieren
    for chap in data_structure:
        for tab in data_structure[chap]:
            data_structure[chap][tab].sort(key=lambda x: x['index'])

    js_content = f"const audioData = {json.dumps(data_structure, indent=4)};"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Erfolg! {count} Dateien verarbeitet. D1.1 sollte jetzt dabei sein.")

except FileNotFoundError:
    print(f"Fehler: Datei '{input_filename}' nicht gefunden.")