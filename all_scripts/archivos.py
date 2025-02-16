from all_scripts import astrometria as astrom
from all_scripts import todas_las_rutas as r
from rich.live import Live
from rich.console import Console
from rich.text import Text
from rich.progress import Progress
from time import sleep
import rich 
import os
import subprocess
import json
import glob
import shutil
import sys



# Variable global para la ruta principal de la organización de carpetas
route = r.route
imagenes_cortadas = r.imagenes_cortadas
archivo_catalogo = r.archivo_catalogo
threshold = 1500#variable para cambiar la cantidad de recortes que se guardan
def contar_fits():
    """
    Cuenta cuántos archivos .fits hay en el directorio 'route/imagenes_cortadas'.
    """
    return len(glob.glob(imagenes_cortadas + "/*.fits"))
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
    comando = f"find {r.route} -type f -name '*{tipo_de_archivo}' ! -name 'datos_gaia3edr.csv' -exec mv {{}} \"{dest_dir}\" \\;"
    
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
    if os.path.exists(destination_file):
         os.remove(destination_file)   
    # Move the file from the source to the destination.
    try:
        shutil.move(source_file, destination_file)
        print(f"File '{source_file}' has been moved to '{destination_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")
def ejecutar_sh(archivo_a_ejecutar):
    '''La función ejecutar_sh ejecuta todos los comandos de un archivos 
        recibe un archivo .txt o .sh'''
    with open(archivo_a_ejecutar, "r", encoding="utf-8") as archivo_leido:
            for i, linea in enumerate(archivo_leido):
                linea = linea.strip()
                subprocess.run(linea,shell=True, check=True, text=True)
def barra_de_progreso(actual,valor_total,texto_de_barra="Donwloading...",color="red"):
     progress = Progress()
     texto_barra_completo = f"[{color}]{texto_de_barra}"
     with progress:
                # Create a task with total equal to the threshold.
                task = progress.add_task(texto_barra_completo, total=valor_total)
                # Update the task to reflect the current count.
                progress.update(task, completed=actual)
                # Brief pause to allow the progress bar to be visible.
                import time
                time.sleep(0.5)    
def ejecutar_curl_desde_archivo():
    """
    Executes curl commands from a shell file one by one, starting from the line number
    stored in "info.json" (under the key "start"). After executing each curl command,
    it calls astrom.cortarImagen(name) to process the downloaded image.
    If that function returns True, the JSON file is updated with the current line number.
    """
    coordenadas = astrom.get_coordinates_from_name("algol")
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
    total_imagenes = len(glob.glob(os.path.join(r.imagenes_cortadas, "*.fits")))
    if total_imagenes < threshold:
        actualizar_progreso(True)
        
        with open(archivo_sh, "r", encoding="utf-8") as archivo:
            for i, linea in enumerate(archivo):
                if i < start_line + 1:
                    continue  # Skip lines before the stored start
                
                linea = linea.strip()
                print(f"Executing curl command at line {i}: {linea}")
                try:
                 # Update the live display with the current status.
                        sleep(1)
                        with open(info_json, "w") as f_out:
                            json.dump({"start": i}, f_out)
                        subprocess.run("clear", shell=True, check=True, text=True)
                        actualizar_progreso(True)
                        subprocess.run(linea, shell=True, check=True, text=True)
                        
                except subprocess.CalledProcessError as e:
                    print(f"Error executing line {i}: {linea}. Error: {e}")
                
                # Process the downloaded image by calling your function
        
                match = astrom.cortarImagen(coordenadas)
                if match:
                    value = actualizar_progreso(False)
                    # If a match is found, update the JSON with the current line number.
                    if value >= threshold:
                        break
                    try:
               
                        with open(info_json, "w") as f_out:
                            json.dump({"start": i}, f_out)
                        print(f"Updated 'start' in {info_json} to {i}.")
                    except Exception as e:
                        print(f"Error updating {info_json}: {e}")
    else:
        print("ya se cuenta con todas las imagenes deseadas")
def actualizar_progreso(value):
    """
    Counts the number of .fits files in the 'imagenes_cortadas' directory and returns that count.
    If 'value' is True, it displays a progress bar using Rich's Progress that updates once with the current count.
    """
    current = len(glob.glob(os.path.join(route, "imagenes_cortadas", "*.fits")))
    text = Text( f"Progreso: {current}/{threshold} images downloaded."
    )
    text.stylize("bold blue on green")
    rich.print(text)
    barra_de_progreso(current,threshold)
    return current


