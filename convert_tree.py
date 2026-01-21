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
            if len(row) >= 3: # Sicherstellen, dass genügend Spalten vorhanden sind
                csv_id_with_chapter = row[1].strip() # z.B. "C1.1-Vok-A", "C1.1-2a", "D1.1-Vok"
            if len(row) >= 3:  # Sicherstellen, dass genügend Spalten vorhanden sind
                csv_id_raw = row[1].strip()  # z.B. "C1.1-Vok-A", "Neue Vokabeln A", "C1.1-2a", "D1.1-1", "Neue Vokabeln"
                
                # Kapitelnamen aus der CSV-ID extrahieren (z.B. "C1.1" aus "C1.1-Vok-A")
                chapter_in_csv_id_match = re.match(r'([A-Z]\d+\.\d+)', csv_id_with_chapter)
                # Kapitelnamen aus row[1] extrahieren (z.B. "C1.1" aus "C1.1-Vok-A")
                chapter_in_csv_id_match = re.match(r'([A-Z]\d+\.\d+)', csv_id_raw)
                csv_chapter_name = chapter_in_csv_id_match.group(1) if chapter_in_csv_id_match else None

                # Den "table"-Teil aus der CSV-ID extrahieren (z.B. "Vok-A" aus "C1.1-Vok-A")
                # Dieser Teil muss mit dem "table"-Teil übereinstimmen, der aus den Audio-Dateinamen extrahiert wird
                table_part_from_csv = re.sub(r'^[A-Z]\d+\.\d+-', '', csv_id_with_chapter)
                # Den Teil nach dem Kapitelpräfix aus row[1] extrahieren
                table_id_from_csv_without_chapter = re.sub(r'^[A-Z]\d+\.\d+-', '', csv_id_raw)
                
                # "Vokabeln " zu "Vok-" standardisieren und Leerzeichen durch Bindestriche ersetzen
                # Dies gewährleistet die Konsistenz mit der Extraktion des "table"-Teils aus Dateinamen
                clean_table_id = table_part_from_csv.replace('Vokabeln ', 'Vok-').replace(' ', '-')
                # Standardisiere "Neue Vokabeln X" zu "Vok-X" und "Neue Vokabeln" zu "Vok"
                clean_table_id_for_key = table_id_from_csv_without_chapter
                if clean_table_id_for_key.startswith('Neue Vokabeln '):
                    clean_table_id_for_key = clean_table_id_for_key.replace('Neue Vokabeln ', 'Vok-')
                elif clean_table_id_for_key == 'Neue Vokabeln':
                    clean_table_id_for_key = 'Vok'
                
                # --- Spezifische Korrektur für bekannte Inkonsistenzen (CSV-ID ist Zahl, Audio ist Vok) ---
                # Wenn es sich um einen Vokabel-Eintrag handelt (erkennbar an 'Vokabeln' im Titel)
                # und die bereinigte ID eine Ziffer ist, aber die Audio-Dateien 'Vok' verwenden,
                # dann überschreibe die ID für den Schlüssel mit 'Vok'.
                if 'Vokabeln' in row[2] and clean_table_id_for_key.isdigit():
                    clean_table_id_for_key = 'Vok'
                # --- Ende spezifische Korrektur ---
                
                # Den ursprünglichen ID (row[1]) mit dem Titel (row[2]) kombinieren, wie vom Benutzer gewünscht
                combined_title = f"{row[1].strip()},{row[2].strip()}"
                combined_title = f"{row[1].strip()}, {row[2].strip()}" # Komma und Leerzeichen

                if csv_chapter_name:
                    # Einen eindeutigen Schlüssel aus Kapitelnamen und bereinigter Tabellen-ID erstellen
                    unique_key = f"{csv_chapter_name}_{clean_table_id}"
                    unique_key = f"{csv_chapter_name}_{clean_table_id_for_key}"
                    print(f"DEBUG: Mapping '{unique_key}' to '{combined_title}'")
                    title_map[unique_key] = combined_title
                else:
                    # Fallback für Einträge ohne klares Kapitelpräfix in row[1]
                    # Dies könnte passieren, wenn row[1] nur "Vok" oder "Integration" ist
                    print(f"DEBUG: Kein Kapitelpräfix in '{csv_id_with_chapter}' gefunden. Verwende '{clean_table_id}' als Schlüssel. Mapping zu '{combined_title}'")
                    title_map[clean_table_id] = combined_title # Dies könnte immer noch zu Überschreibungen führen, wenn clean_table_id nicht global eindeutig ist

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
            # Erstelle den gleichen eindeutigen Schlüssel wie oben
            unique_key = f"{chapter_name}_{table}"
            print(f"DEBUG: Looking up table with key '{unique_key}'. Result: '{title_map.get(unique_key, table)}'")
            display_title = title_map.get(unique_key, table)

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

    # Die Top-Level-Kapitel sortieren (z.B. C1.1, C1.2, D1.1)
    sorted_chapter_names = sorted(data_structure.keys())
    sorted_data_structure = {key: data_structure[key] for key in sorted_chapter_names}
    data_structure = sorted_data_structure

    # Die Schlüssel (display_titles) innerhalb jedes Kapitels sortieren
    for chap in data_structure:
        sorted_display_titles = sorted(data_structure[chap].keys())
        data_structure[chap] = {key: data_structure[chap][key] for key in sorted_display_titles}
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
