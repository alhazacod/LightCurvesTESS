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
    Ejecuta directamente el script de Python 'consultas.py' (ubicado en la carpeta python_scripts)
    en lugar del script de Bash.
    """

    try:
        result = subprocess.run(["python3", route + "consultas.py"],
                                capture_output=True, text=True, check=True)
        print("El script recortes.py se ejecutó correctamente.")
        print("Salida estándar:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar recortes.py:")
        print(e.stderr)
def ejecutar_fotometria():
    """
    Ejecuta directamente el script de Python 'consultas.py' y phot.py (ubicado en la carpeta python_scripts)
    en lugar del script de Bash.
    """
    print("se ha alcanzado el limite de recortes, se procede a realizar la fotometría de cada uno")
    ejecutar_consultas()
    try:
        result = subprocess.run(["python3", route + "phot.py"],
                                capture_output=True, text=True, check=True)
        print("El script recortes.py se ejecutó correctamente.")
        print("Salida estándar:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar recortes.py:")
        print(e.stderr)

def mover_fits():
    """
    Ejecuta el comando find para mover todos los archivos .fits al directorio 'route/imagenes_cortadas'.

    El comando utilizado es:
      find {route} -type f -name '*.fits' -exec mv {} "{route}imagenes_cortadas" \;

    Se utiliza shell=True para que se interprete correctamente la cadena del comando.
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
    Ejecuta el script bash especificado en 'script_path' y muestra la salida.
    
    Parámetros:
      - script_path (str): La ruta del script bash que se desea ejecutar.
    
    Se asume que el script tiene permisos de ejecución. Si no es así, se fuerza su ejecución mediante bash.
    """
    print("Iniciando Descargas")
    try:
        result = subprocess.run(["bash", script_path],
                                capture_output=True, text=True, check=True)
        print("El script se ejecutó correctamente.")
        print("Salida estándar:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el script:")
        print(e.stderr)

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
      2. Se copia cada línea del archivo original.
         - Después de la primera línea (índice 0) se añade "python3 consultas.py"
           y después de la segunda línea (índice 1) se añade "python3 recortes.py".
      3. Al final del archivo se añade la línea:
         find . -name '*.fits' -mv "{route}ImagenesSinCortar"
    
    Retorna:
        list: Una lista con las líneas procesadas.
    """
    # Si el archivo nuevo ya existe, se elimina
    if os.path.exists(ruta_archivo_nuevo):
        os.remove(ruta_archivo_nuevo)
    
    lineas_procesadas = []
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()
    
    for i, linea in enumerate(lineas):
        linea = linea.rstrip("\n")
        lineas_procesadas.append(linea + "\n")
        if i != 0:
            lineas_procesadas.append("recortes.py\n")
        else:
            lineas_procesadas.append("python3 consultas.py\n")
    
    with open(ruta_archivo_nuevo, 'w', encoding='utf-8') as nuevo_archivo:
        nuevo_archivo.writelines(lineas_procesadas)
    
    return lineas_procesadas

# Bloque principal: se usan las rutas construidas a partir de la variable global 'route'
if __name__ == "__main__":
    if contar_fits() >= 3:
        ejecutar_fotometria()

    else:
        ejecutar_consultas()
        ejecutar_script_bash(route + "bash_scripts/comandosCurl_modificado.sh")
        archivo_original = route + "bash_scripts/comandosCurl"           # Archivo original
        archivo_nuevo = route + "bash_scripts/comandosCurl_modificado.sh"  # Archivo nuevo a generar
        almacenarScript(archivo_original, archivo_nuevo)
        aplicar_chmod()
        ejecutar_script_bash(route + "bash_scripts/comandosCurl_modificado.sh")
