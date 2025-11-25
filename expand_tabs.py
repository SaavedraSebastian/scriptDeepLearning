import json
import os

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
        raise ValueError("El archivo JSON no contiene la sección 'tabs'.")

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

    print(f"Archivo expandido generado en: {output_path}")

if __name__ == "__main__":
    print("=== Expansor de TABS ===")
    
    file_name = input("Escribe el nombre del archivo JSON (ej: V101.json): ").strip()

    input_path = os.path.join("json", file_name)

    if not os.path.exists(input_path):
        print(f"No se encontró el archivo en: {input_path}")
        print("Asegúrate de colocar tus JSON dentro de la carpeta: json/")
        exit(1)

    expand_tabs(input_path)