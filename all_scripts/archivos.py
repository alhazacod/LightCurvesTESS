from all_scripts import astrometria as astrom
from all_scripts import todas_las_rutas as ru
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
import time


# Variable global para la ruta principal de la organización de carpetas
route = ru.route
imagenes_cortadas = ru.imagenes_cortadas
archivo_catalogo = ru.archivo_catalogo
threshold = 1500#variable para cambiar la cantidad de recortes que se guardan
import re

def organizar_comandos_por_fecha(output_filename="comandos_curl_ordenados.txt"):
    """
    Lee el archivo de comandos curl, extrae la parte numérica que representa la fecha
    (de la forma "-o tess<FECHA>-...") y organiza los comandos en orden ascendente según esa fecha.
    
    Parámetros:
      input_filename (str): Nombre del archivo original de comandos.
      output_filename (str): Nombre del archivo en el que se guardarán los comandos ordenados.
    """
    input_filename=f"{ru.bash_scripts}comandos_curl.txt"
    # Leer todas las líneas del archivo de comandos.
    with open(input_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Filtrar únicamente las líneas que contengan comandos curl.
    curl_lines = [line.strip() for line in lines if line.strip().startswith("curl")]
    
    # Función auxiliar para extraer la fecha del nombre de archivo.
    def extraer_fecha(line):
        # Se busca el patrón: -o tess<FECHA>-...
        match = re.search(r'-o\s+tess(\d+)-', line)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return 0
        return 0

    # Ordenar las líneas según la fecha extraída.
    comandos_ordenados = sorted(curl_lines, key=extraer_fecha)
    
    # Escribir los comandos ordenados en un nuevo archivo.
    with open(output_filename, "w", encoding="utf-8") as f:
        # Si se desea conservar el shebang inicial, se puede agregar.
        f.write("#!/bin/sh\n")
        for comando in comandos_ordenados:
            f.write(comando + "\n")
    mover_objeto(output_filename,ru.bash_scripts)
    print(f"Comandos organizados por fecha y guardados en {output_filename}")

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
    tipo_de_archivo = route + "*"+tipo_de_archivo
    # Crear el directorio destino si no existe
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    type_files = glob.glob(tipo_de_archivo)
    for individual_file in type_files:
        mover_objeto(individual_file,dest_dir)
def creacion_directorio(directorio):
      if not os.path.exists(directorio):
        os.makedirs(directorio)
     
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
     subprocess.run("clear", shell=True, check=True, text=True)
     progress = Progress()
     texto_barra_completo = f"[{color}]{texto_de_barra}"
     print(f"van {actual}/{valor_total}")
     with progress:
                # Create a task with total equal to the threshold.
                task = progress.add_task(texto_barra_completo, total=valor_total)
                # Update the task to reflect the current count.
                progress.update(task, completed=actual)
                # Brief pause to allow the progress bar to be visible.
                import time
                time.sleep(0.5)    
def actualizar_progreso(value):
    """
    Cuanto el numero de .fits en el directorio'imagenes cortadas'
    Si 'value' es True, muestra la barra de progreso unsando la función barra_de_progreso(valor_actual,valor_total)
    """
    
    current = len(glob.glob(os.path.join(route, "imagenes_cortadas", "*.fits")))
    if value:
        barra_de_progreso(current,threshold)
    return current

def call_json(info_json):
    with open(info_json, "r") as f:
        info = json.load(f)
    start_line = info.get("start", 0)
    return start_line
     


def update_json(info_json, i):
    """Updates the JSON file with the current line number."""
    try:
        with open(info_json, "w") as f_out:
            json.dump({"start": i}, f_out)
        print(f"Updated 'start' in {info_json} to {i}.")
    except Exception as e:
        print(f"Error writing to {info_json}: {e}")

def call_json(info_json):
    """Reads the 'start' value from the JSON file."""
    try:
        with open(info_json, "r") as f_in:
            data = json.load(f_in)
        return data.get("start", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0  # Default to 0 if file doesn't exist or is invalid

def secuencia_de_descarga_y_recorte(coordenadas, i, linea, info_json):
    """Executes curl command, downloads images, and processes them."""
    directorio_destino = ru.imagenes  # Ensure this is a valid directory
    print(f"Executing curl command at line {i}: {linea}")
    actualizar_progreso(True)
    try:
        time.sleep(1)  # Simulate processing time
        update_json(info_json, i)

        # Run the curl command
        proceso = subprocess.run(
            f"{linea} -o {directorio_destino}",
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=ru.imagenes
        )

        if proceso.returncode != 0:
            print(f"Error executing line {i}: {linea}. Error: {proceso.stderr.decode().strip()}")
            return

    except Exception as e:
        print(f"Exception while executing line {i}: {linea}. Error: {e}")
        return

    # Process downloaded images
    actualizar_progreso(True)
    fits_files = glob.glob(os.path.join(directorio_destino, "*.fits"))
    for individual_file in fits_files:
        match = astrom.cortarImagen(coordenadas, individual_file)
        if match:
            value = actualizar_progreso(False)
            if value >= threshold:
                break
            try:
                update_json(info_json, i)
            except Exception as e:
                print(f"Error updating {info_json}: {e}")

def ejecutar_curl_desde_archivo():
    """Executes curl commands from a file, resuming from the last recorded line."""
    coordenadas = astrom.get_coordinates_from_name("algol")
    info_json = "info.json"

    # Read the last processed line number
    start_line = call_json(info_json)
    print(f"Starting from line: {start_line}")

    archivo_sh = os.path.join(ru.bash_scripts, "comandos_curl_ordenados.txt")
    total_imagenes = len(glob.glob(os.path.join(ru.imagenes_cortadas, "*.fits")))

    if total_imagenes < threshold:
       

        try:
            with open(archivo_sh, "r", encoding="utf-8") as archivo:
                for i, linea in enumerate(archivo):
                    if i < start_line:
                        continue  # Corrected: Only skip up to start_line

                    linea = linea.strip()
                    secuencia_de_descarga_y_recorte(coordenadas, i, linea, info_json)

        except FileNotFoundError:
            print(f"Error: The file {archivo_sh} was not found.")
    else:
        print("All desired images are already available.")
