from all_scripts import astrometria as astrom
import os
import subprocess
import json
import glob
import shutil


# Variable global para la ruta principal de la organización de carpetas
route = "./"
threshold = 20#variable para cambiar la cantidad de recortes que se guardan
#las primeras 77 se guardaron sin generar errores de buffer


def contar_fits():
    """
    Cuenta cuántos archivos .fits hay en el directorio 'route/imagenes_cortadas'.
    """
    return len(glob.glob(route + "imagenes_cortadas/*.fits"))
def mover_objetos(tipo_de_archivo, directorio_de_destino):
    """
    Mueve todos los archivos con la extensión especificada a un directorio de destino,
    omitiendo el archivo 'datos_gaia3edr.csv'.

    Parámetros:
      tipo_de_archivo (str): La extensión del archivo (por ejemplo, ".csv" o ".fits").
      directorio_de_destino (str): El directorio donde se moverán los archivos.
    
    """
    dest_dir = route + directorio_de_destino
    # Crear el directorio destino si no existe
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Construir el comando find:
    # - Busca en el directorio actual todos los archivos cuyo nombre termine en tipo_de_archivo.
    # - Excluye (con !) el archivo 'datos_gaia3edr.csv'.
    # - Para cada archivo encontrado se ejecuta el comando mv para moverlo al directorio de destino.
    comando = f"find ./ -type f -name '*{tipo_de_archivo}' ! -name 'datos_gaia3edr.csv' -exec mv {{}} \"{dest_dir}\" \\;"
    
    print(f"Moviendo los archivos tipo {tipo_de_archivo} a {directorio_de_destino}...")
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print(f"Error al mover archivos {tipo_de_archivo}:")
        print(resultado.stderr)
    else:
        print(f"Archivos {tipo_de_archivo} movidos correctamente.")
def mover_objeto(nombre_de_archivo, directorio_de_destino):
    """
    Mueve el archivo especificado a un directorio de destino.

    Parámetros:
      nombre_de_archivo (str): El nombre del archivo (por ejemplo, "gaia3edr.csv" o "tess.fits").
      directorio_de_destino (str): El directorio donde se moverán los archivos.
    """
    source_file = nombre_de_archivo
    # Use os.path.join to construct the destination directory path.
    destination_dir = os.path.join(route, directorio_de_destino)
    
    # Create the destination directory if it doesn't exist.
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    
    # Construct the full destination path for the file.
    destination_file = os.path.join(destination_dir, os.path.basename(source_file))
    
    # Move the file from the source to the destination.
    try:
        shutil.move(source_file, destination_file)
        print(f"File '{source_file}' has been moved to '{destination_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

def ejecutar_curl_desde_archivo():
    """
    Executes curl commands from a shell file one by one, starting from the line number
    stored in "info.json" (under the key "start"). After executing each curl command,
    it calls astrom.cortarImagen(name) to process the downloaded image.
    If that function returns True, the JSON file is updated with the current line number.
    """
    info_json = "info.json"
    # Read the starting line from the JSON file
    try:
        with open(info_json, "r") as f:
            info = json.load(f)
        start_line = info.get("start", 0)
    except Exception as e:
        print(f"Could not read {info_json} (using start=0). Error: {e}")
        start_line = 0

    print(f"Starting from line: {start_line}")

    # Define the shell file containing the curl commands.
    archivo_sh = os.path.join(route, "bash_scripts", "comandos_curl.txt")
    actualizar_progreso()
    
    with open(archivo_sh, "r", encoding="utf-8") as archivo:
        for i, linea in enumerate(archivo):
            if i < start_line + 1:
                continue  # Skip lines before the stored start
            
            linea = linea.strip()
            print(f"Executing curl command at line {i}: {linea}")
            try:
                subprocess.run(linea, shell=True, check=True, text=True)
            except subprocess.CalledProcessError as e:
                print(f"Error executing line {i}: {linea}. Error: {e}")
            
            # Process the downloaded image by calling your function
    
            match = astrom.cortarImagen("algol")
            if match:
                actualizar_progreso()
                # If a match is found, update the JSON with the current line number.
                try:
                    with open(info_json, "w") as f_out:
                        json.dump({"start": i}, f_out)
                    print(f"Updated 'start' in {info_json} to {i}.")
                except Exception as e:
                    print(f"Error updating {info_json}: {e}")

def actualizar_progreso():
    """
    Cuenta el numero de imagenes .fits que hay en el directorio imagenes cortadas y retorna la cantidad  de imagenes que hay sobre el numero de imagenes requeridas para graficar en la curva de luz.
    """
    dest_dir = os.path.join(route, "imagenes_cortadas")
    current = len(glob.glob(os.path.join(dest_dir, "*.fits")))
    print(f"Progress: {current}/{threshold} images downloaded.")
    return current
