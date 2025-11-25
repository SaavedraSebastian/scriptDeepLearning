import json
import os
import glob

def format_compact_json(obj, indent=2):
    if isinstance(obj, dict):
        items = []
        for key, value in obj.items():
            formatted_value = format_compact_json(value, indent)
            items.append(f'{" " * indent}"{key}": {formatted_value}')
        return "{\n" + ",\n".join(items) + "\n}"
    
    elif isinstance(obj, list):
      
        if all(isinstance(item, (int, float)) for item in obj):
            return "[" + ", ".join(map(str, obj)) + "]"
        else:
            items = [format_compact_json(item, indent + 2) for item in obj]
            return "[\n" + ",\n".join(items) + f"\n{' ' * indent}]"
    
    elif isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    
    else:
        return json.dumps(obj)


def expand_tabs(input_path):
 
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    name = data.get("name", "archivo")
    fps = data.get("fps")
    total_frames = data.get("frames")
    song_data = data.get("song_data", {})
    tabs = data.get("tabs", [])

    if not tabs:
        raise ValueError(f"ERROR: El archivo '{input_path}' no contiene 'tabs'.")


    tabs_sorted = sorted(tabs, key=lambda x: x["frame"])

    expanded_tabs = []
    last = tabs_sorted[0]


    for f in range(1, total_frames + 1):
        found = next((t for t in tabs_sorted if t["frame"] == f), None)
        if found:
            last = found

        expanded_tabs.append({
            "frame": f,
            "freets": last["freets"],
            "actions": last["actions"],
            "chord": last["chord"]
        })

    output_data = {
        "name": name,
        "fps": fps,
        "frames": total_frames,
        "song_data": song_data,
        "tabs": expanded_tabs
    }

    output_folder = "etiquetas"
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, f"{name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        formatted_json = format_compact_json(output_data)
        f.write(formatted_json)

    print(f"Archivo expandido: {output_path}")


def process_all_files():
    print("=== EXPANSOR DE TABS (MÚLTIPLES ARCHIVOS) ===")

    json_files = glob.glob(os.path.join("json", "*.json"))

    if not json_files:
        print("No se encontraron archivos en la carpeta 'json/'.")
        return

    print(f"Encontrados {len(json_files)} archivos para expandir:\n")

    for f in json_files:
        print(" →", os.path.basename(f))

    print("\nProcesando...\n")

    for f in json_files:
        try:
            expand_tabs(f)
        except Exception as e:
            print(f"Error procesando {f}: {e}")

    print("\nProceso completado.")


if __name__ == "__main__":
    process_all_files()
