import json
import os
import re
import glob

def compact_json_lists(json_string):

    def compact_array(match):
        array_content = match.group(1)
        cleaned = re.sub(r'\s+', ' ', array_content).strip()
        return f"[{cleaned}]"
    
    pattern = r'\[\s*([^\[\]]*?)\s*\]'
    result = re.sub(pattern, compact_array, json_string, flags=re.DOTALL)
    
    return result

def reverse_labels(input_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    name = data["name"]
    fps = data["fps"]
    total_frames = data["frames"]
    song_data = data["song_data"]
    tabs = data["tabs"]

    reversed_tabs = []

    for t in tabs:
        old_frame = t["frame"]
        new_frame = total_frames - old_frame

        reversed_tabs.append({
            "frame": new_frame,
            "freets": t["freets"],
            "actions": t["actions"],
            "chord": t["chord"]
        })

    reversed_tabs = sorted(reversed_tabs, key=lambda x: x["frame"])

    output_data = {
        "name": f"{name}",
        "fps": fps,
        "frames": total_frames,
        "song_data": song_data,
        "tabs": reversed_tabs
    }

    output_folder = "etiquetas_reversed"
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, f"{name}.json")

    raw_json = json.dumps(output_data, indent=2, ensure_ascii=False, sort_keys=False)
    
    compact_json = compact_json_lists(raw_json)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(compact_json)

    print(f"{name}.json generado")
    return len(reversed_tabs)

def process_multiple_files():

    input_folder = "etiquetas"
    output_folder = "etiquetas_reversed"

    os.makedirs(output_folder, exist_ok=True)

    json_pattern = os.path.join(input_folder, "*.json")
    json_files = glob.glob(json_pattern)

    if not json_files:
        print("No se encontraron archivos JSON en la carpeta 'etiquetas'")
        return
    
    print(f"Procesando {len(json_files)} archivos encontrados...")

    total_tabs = 0

    for file_path in json_files:
        try:
            tabs_procesados = reverse_labels(file_path)
            total_tabs += tabs_procesados
        except Exception as e:
            print(f"Error procesando {os.path.basename(file_path)}: {e}")

    print("\nProceso completado!")

if __name__ == "__main__":
    print("=== INVERSOR DE ETIQUETAS (MÚLTIPLES ARCHIVOS) ===")
    print("Este script procesa múltiples archivos JSON a la vez")
    print()
    
    process_multiple_files()