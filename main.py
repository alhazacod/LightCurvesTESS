import os
import subprocess
import glob
import shutil

# Variable global para la ruta principal de la organización de carpetas
route = "./"

def contar_fits():
    """
    Cuenta cuántos archivos .fits hay en el directorio 'route/imagenes_cortadas'.
    """
    return len(glob.glob(route + "imagenes_cortadas/*.fits"))
def ejecutar_consultas():
    """
    Ejecuta directamente el script de Python 'consultas.py' (ubicado en la carpeta principal)
    """
    try:
        subprocess.run(["python3", route + "consultas.py"], check=True)
        print("El script consultas.py se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar consultas.py:")
        print(e)
def ejecutar_fotometria():
    """
    Ejecuta directamente los scripts 'consultas.py' y 'phot.py' para proceder con la fotometría.
    """
    print("Se ha alcanzado el límite de recortes, se procede a realizar la fotometría.")
    ejecutar_consultas()
    try:
        subprocess.run(["python3", route + "phot.py"], check=True)
        print("El script phot.py se ejecutó correctamente.")
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar phot.py:")
        print(e)
def mover_fits():
    """
    Ejecuta el comando find para mover todos los archivos .fits al directorio 'route/imagenes_cortadas'.
    """
    comando = f"find {route} -type f -name '*.fits' -exec mv {{}} \"{route}imagenes_cortadas\" \\;"
    print("Moviendo las imágenes descargadas...")
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    if resultado.returncode != 0:
        print("Error al mover archivos .fits:")
        print(resultado.stderr)
    else:
        print("Archivos .fits movidos correctamente.")
def ejecutar_script_bash(script_path):
    """
    Ejecuta el script Bash especificado en 'script_path' y muestra la salida en tiempo real.
    
    Se asume que el script tiene permisos de ejecución. Si no es así, se fuerza su ejecución mediante bash.
    """
    print("Iniciando Descargas desde el script Bash...")
    try:
        subprocess.run(["bash", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script Bash:")
        print(e)

def aplicar_chmod():
    """
    Ejecuta el comando 'chmod +x {route}bash_scripts/comandosCurl_modificado.sh'
    para asignar permisos de ejecución al archivo.
    """
    comando = ["chmod", "+x", route + "bash_scripts/comandosCurl_modificado.sh"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    if resultado.returncode != 0:
        print("Error al aplicar chmod:", resultado.stderr)
    else:
        print("Permisos aplicados correctamente.")

def almacenarScript(ruta_archivo, ruta_archivo_nuevo):
    """
    Lee el archivo especificado en 'ruta_archivo' y crea un nuevo archivo en 'ruta_archivo_nuevo'
    con las siguientes modificaciones:
      1. Si el archivo nuevo existe, se borra antes de crearlo.
      2. Se inserta AL INICIO (después del shebang, si existe) la línea que ejecuta el script de limpieza
         (ubicado en "./bash_scripts/limpieza.sh") y se inicializan las variables:
            counter=0
            threshold=<valor deseado>
      3. Luego, para cada línea del archivo original se copia la línea y se añade la ejecución del comando:
         - En la primera línea se añade "python3 consultas.py".
         - En las siguientes se añade "python3 recortes.py".
      4. Inmediatamente después de cada comando se inserta un bloque que:
            - Incrementa el contador (o, alternativamente, vuelve a contar los archivos en imagenes_cortadas).
            - Imprime el progreso en el formato "Progress: $current/[threshold] images downloaded".
            - Si el número actual de archivos alcanza o supera el umbral, imprime un mensaje y ejecuta exit 0.
    
    Retorna:
        list: Una lista con las líneas procesadas.
    """
    # Si el archivo nuevo ya existe, se elimina
    if os.path.exists(ruta_archivo_nuevo):
        os.remove(ruta_archivo_nuevo)
    
    lineas_procesadas = []
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()
    
    # Definir el umbral (threshold) de archivos .fits en la carpeta imagenes_cortadas
    threshold = 30 # Modifica este valor según sea necesario
    
    # Bloque único al inicio: Si existe un shebang, conservarlo
    if lineas and lineas[0].startswith("#!"):
        lineas_procesadas.append(lineas[0])
        rest_lines = lineas[1:]
    else:
        rest_lines = lineas
    
    # Inserción única: llamada al script de limpieza y la inicialización de variables
    lineas_procesadas.append("bash ./bash_scripts/limpieza.sh\n")
    lineas_procesadas.append("counter=0\n")
    lineas_procesadas.append("threshold=" + str(threshold) + "\n")
    
    # Para cada línea restante del archivo original
    for i, linea in enumerate(rest_lines):
        linea = linea.rstrip("\n")
        # Agregar la línea original (por ejemplo, el comando curl)
        lineas_procesadas.append(linea + "\n")
        
        # Inserción de la ejecución del comando deseado según la posición:
        if i == 0:
            lineas_procesadas.append("python3 consultas.py\n")
        else:
            lineas_procesadas.append("python3 recortes.py\n")
        
        # Bloque para actualizar el progreso basado en la cantidad de archivos .fits en imagenes_cortadas:
        # Aquí se vuelve a contar los archivos en lugar de usar un contador interno, para reflejar el estado real.
        progress_block = [
            'current=$(find ' + route + 'imagenes_cortadas -maxdepth 1 -type f -name "*.fits" | wc -l)\n',
            'echo "Progress: $current/' + str(threshold) + ' images downloaded."\n',
            'if [ $current -ge ' + str(threshold) + ' ]; then\n',
            '    echo "Threshold reached. Exiting script."\n',
            '    exit 0\n',
            'fi\n'
        ]
        lineas_procesadas.extend(progress_block)
    
    with open(ruta_archivo_nuevo, 'w', encoding='utf-8') as nuevo_archivo:
        nuevo_archivo.writelines(lineas_procesadas)
    
    return lineas_procesadas

# Bloque principal: se usan las rutas construidas a partir de la variable global 'route'
if __name__ == "__main__":
    
        # Primero se ejecuta consultas.py (opcional, según tu flujo)
        ejecutar_consultas()
        # Generar el script modificado a partir del original
        archivo_original = route + "bash_scripts/comandosCurl"           # Archivo original
        archivo_nuevo = route + "bash_scripts/comandosCurl_modificado.sh"  # Archivo nuevo a generar
        almacenarScript(archivo_original, archivo_nuevo)
        aplicar_chmod()
        # Ejecutar el script modificado (se mostrará el progreso y, al alcanzar el umbral, se saldrá)
        ejecutar_script_bash(archivo_nuevo)
        # Una vez que el script de Bash se detenga por alcanzar el umbral, se procede a fotometría
        ejecutar_fotometria()
