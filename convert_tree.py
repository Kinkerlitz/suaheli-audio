import re
import json
import os
import csv

input_filename = 'tree_tts.txt'
output_filename = 'audio_data.js'
title_map_filename = 'Tabellenübersicht aus Dokument - Tabellenübersicht aus Dokument.csv'

data_structure = {}
title_map = {}

# Lade die Titel-Übersetzungen aus der CSV
try:
    with open(title_map_filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Header-Zeile überspringen
        for row in reader:
            if len(row) >= 3:
                # Bereinige die ID, um sie mit den Dateinamen-Teilen abgleichen zu können
                # "Neue Vokabeln A" -> "Vok-A"
                # "C1.1-2a" -> "2a"
                raw_id = row[1].replace('Neue Vokabeln', 'Vok').replace('.', '_')
                
                # Entferne den Kapitel-Präfix (z.B. C1_1-)
                clean_id = re.sub(r'^[A-Z]\d+_\d+-', '', raw_id)
                
                # Standardisiere "Vokabeln X" zu "Vok-X" und ersetze Leerzeichen durch Bindestriche
                clean_id = clean_id.replace('Vokabeln ', 'Vok-').replace(' ', '-')
                
                print(f"DEBUG: Mapping '{clean_id}' to '{row[2].strip()}'")
                title_map[clean_id] = row[2].strip()
except FileNotFoundError:
    print(f"⚠️ WARNUNG: Die Titel-Datei '{title_map_filename}' wurde nicht gefunden. Fallback auf technische Namen.")

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
            index = int(match.group(3))  # z.B. 1
            filename = match.group(0)    # ganzer Dateiname
            
            chapter_name = get_clean_chapter_name(raw_chapter) # C1.1
            
            # Hole den beschreibenden Titel aus der Map, ansonsten nimm den technischen Namen
            print(f"DEBUG: Looking up table '{table}' for chapter '{chapter_name}'. Result: '{title_map.get(table, table)}'")
            display_title = title_map.get(table, table)

            # Struktur sicherstellen
            if chapter_name not in data_structure:
                data_structure[chapter_name] = {}
            
            if display_title not in data_structure[chapter_name]:
                data_structure[chapter_name][display_title] = []
            
            # Sauberen Eintrag hinzufügen (OHNE Title/Artist Tags)
            data_structure[chapter_name][display_title].append({
                'index': index,
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
