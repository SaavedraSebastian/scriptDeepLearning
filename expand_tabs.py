import json
import os
import glob
import re

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

def extract_number(filename):

    match = re.search(r'V(\d+)\.json$', filename)
    return int(match.group(1)) if match else None

def create_reverse_json(input_path):
 
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filename = os.path.basename(input_path)
    original_number = extract_number(filename)
    if original_number is None:
        print(f"Saltando {filename}: No tiene formato V001.json")
        return

    new_number = original_number + 50
    new_name = f"V{new_number:03d}.json"

    total_frames = data.get("frames", 0)
    tabs = data.get("tabs", [])

    if not tabs:
        print(f" Saltando {filename}: No contiene 'tabs'")
        return

   
    min_frame = min(tab.get("frame", 0) for tab in tabs)
    zero_based = (min_frame == 0)

    reversed_tabs = []
    for tab in tabs:
        original_frame = tab["frame"]
        if zero_based:
            reversed_frame = (total_frames - 1) - original_frame
        else:
            reversed_frame = total_frames - original_frame + 0

        if zero_based:
            reversed_frame = max(0, min(total_frames - 1, reversed_frame))
        else:
            reversed_frame = max(1, min(total_frames, reversed_frame))

        reversed_tabs.append({
            "frame": reversed_frame,
            "freets": tab.get("freets"),
            "actions": tab.get("actions"),
            "chord": tab.get("chord")
        })


    reversed_tabs_sorted = sorted(reversed_tabs, key=lambda x: x["frame"])

    reversed_data = {
        "name": new_name.replace('.json', ''),
        "fps": data.get("fps"),
        "frames": total_frames,
        "song_data": data.get("song_data", {}),
        "tabs": reversed_tabs_sorted
    }

    output_folder = "etiqueta_reverse"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, new_name)

    with open(output_path, "w", encoding="utf-8") as f:
        formatted_json = format_compact_json(reversed_data)
        f.write(formatted_json)

    zb = "0-based" if zero_based else "1-based"
    print(f" {filename} -> {new_name} (invertido, detectado {zb})")


def expand_tabs(input_path, output_folder):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    name = data.get("name", "archivo")
    fps = data.get("fps")
    total_frames = data.get("frames")
    song_data = data.get("song_data", {})
    tabs = data.get("tabs", [])

    if not tabs:
        print(f"  Saltando {name}: No contiene 'tabs'")
        return

    tabs_sorted = sorted(tabs, key=lambda x: x["frame"])
    expanded_tabs = []
    start_frame = tabs_sorted[0]["frame"]
    last = tabs_sorted[0]

    for f in range(start_frame, total_frames + 1):
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

    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f"{name}.json")

    with open(output_path, "w", encoding="utf-8") as f:
        formatted_json = format_compact_json(output_data)
        f.write(formatted_json)

    print(f" Expandido: {name}.json")

def option1_create_reverse():
    print("\n=== OPCIÓN 1: CREAR JSONs INVERTIDOS ===")
    
    json_files = glob.glob(os.path.join("json", "V*.json"))
    json_files.sort()
    
    if not json_files:
        print("No se encontraron archivos V*.json en la carpeta 'json/'.")
        return
    
    print(f"Encontrados {len(json_files)} archivos para invertir:\n")
    
    for f in json_files:
        filename = os.path.basename(f)
        original_number = extract_number(filename)
        if original_number:
            new_number = original_number + 49
            print(f" → {filename} -> V{new_number:03d}.json")
        else:
            print(f" → {filename} (formato no válido)")
    
    print("\nProcesando...\n")
    
    for f in json_files:
        try:
            create_reverse_json(f)
        except Exception as e:
            print(f"Error procesando {f}: {e}")
    
    print(f"\nProceso completado. Archivos invertidos guardados en 'etiqueta_reverse/'")

def option2_expand_both():
    print("\n=== OPCIÓN 2: EXPANDIR JSONs ORIGINALES E INVERTIDOS ===")
    original_files = glob.glob(os.path.join("json", "V*.json"))
    original_files.sort()
    reverse_files = glob.glob(os.path.join("etiqueta_reverse", "V*.json"))
    reverse_files.sort()
    
    if not original_files and not reverse_files:
        print("No se encontraron archivos para expandir.")
        return
    
    print("Archivos a expandir:")
    
    if original_files:
        print("\nORIGINALES (json/):")
        for f in original_files:
            print(f" → {os.path.basename(f)}")
    
    if reverse_files:
        print("\nINVERTIDOS (etiqueta_reverse/):")
        for f in reverse_files:
            print(f" → {os.path.basename(f)}")
    
    print("\nProcesando...\n")

    if original_files:
        print("Expandiendo archivos ORIGINALES:")
        for f in original_files:
            try:
                expand_tabs(f, "etiquetas_expandidas")
            except Exception as e:
                print(f"Error procesando {f}: {e}")
    if reverse_files:
        print("\n Expandiendo archivos INVERTIDOS:")
        for f in reverse_files:
            try:
                expand_tabs(f, "etiquetas_expandidas")
            except Exception as e:
                print(f"Error procesando {f}: {e}")
    
    print(f"\n Proceso completado. Archivos expandidos guardados en 'etiquetas_expandidas/'")

def main():
    print("=== SISTEMA DE EXPANSIÓN DE TABS ===")
    print("1. Crear JSONs invertidos (de json/ a etiqueta_reverse/)")
    print("2. Expandir JSONs originales e invertidos")
    
    try:
        option = input("\nSelecciona una opción (1/2): ").strip()
        
        if option == "1":
            option1_create_reverse()
        elif option == "2":
            option2_expand_both()
        else:
            print("Opción no válida. Debe ser 1 o 2.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()