import os
import subprocess
import os
import subprocess
import glob
route = "./"
def contar_fits():
    """
    Cuenta cuántos archivos .fits hay en el directorio './imagenes_cortadas'.
    """
    return len(glob.glob(f"{route}imagenes_cortadas/*.fits"))


def ejecutar_consultas():
    """
    Ejecuta directamente el script de Python 'consultas.py' en lugar del script de Bash.
    """
    print("Límite de imágenes alcanzado, ejecutando solo consultas.py...")
    try:
        result = subprocess.run(["python3", "consultas.py"],
                                capture_output=True, text=True, check=True)
        print("El script recortes.py se ejecutó correctamente.")
        print("Salida estándar:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar recortes.py:")
        print(e.stderr)

def mover_fits():
    """
    Ejecuta el comando find para mover todos los archivos .fits al directorio "ImagenesSinCortar".

    El comando utilizado es:
      find . -type f -name '*.fits' -exec mv {} "./ImagenesSinCortar" \;

    Se utiliza shell=True para que se interprete correctamente la cadena del comando.
    """
    
    comando = f"find {route} -type f -name '*.fits' -exec mv {{}} \"{route}imagenes_cortadas\" \\;"

    print("moviendo las imagenes descargadas")
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
    
    Se asume que el script tiene permisos de ejecución. Si no es así, se fuerza su ejecución
    mediante bash.
    """
    print("Iniciando Descargas")
    try:
        # Ejecuta el script utilizando 'bash' explícitamente para garantizar su ejecución
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
    Ejecuta el comando 'chmod +x ./bash_scripts/comandosCurl_modificado.sh'
    para asignar permisos de ejecución al archivo.
    """
    comando = ["chmod", "+x", f"{route}bash_scripts/comandosCurl_modificado.sh"]
    resultado = subprocess.run(comando, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        print("Error al aplicar chmod:", resultado.stderr)
    else:
        print("Permisos aplicados correctamente.")

def almacenarScript(ruta_archivo, ruta_archivo_nuevo):
    """
    Lee el archivo especificado en 'ruta_archivo' y crea un nuevo archivo en 'ruta_archivo_nuevo'
    con las siguientes modificaciones:
      1. Si el archivo nuevo existe, se borra antes de crear el nuevo.
      2. Se copia cada línea del archivo original.
         - Justo después de la primera línea (línea 0) no se añade nada.
         - Después de la segunda línea (línea 1) se añade la línea "python3 hola.py".
      3. Al final del archivo se añade la línea:
         find . -name '*.fits' -mv "./ImagenesSinCortar"
    
    Retorna:
        list: Una lista con las líneas procesadas.
    """
    # Si el archivo nuevo ya existe, se elimina
    if os.path.exists(ruta_archivo_nuevo):
        os.remove(ruta_archivo_nuevo)
    
    lineas_procesadas = []
    
    # Leer todas las líneas del archivo original
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        lineas = archivo.readlines()
    
    # Procesar cada línea
    for i, linea in enumerate(lineas):
        # Eliminar salto de línea final para evitar duplicados
        linea = linea.rstrip("\n")
        # Agregar la línea original seguida de un salto de línea
        lineas_procesadas.append(linea + "\n")
        # Después de la segunda línea (índice 1) se añade "python3 hola.py"
        if i != 0:
            lineas_procesadas.append("python3 recortes.py\n")  
        else :
            lineas_procesadas.append("python3 consultas.py\n")  
    # Guardar el contenido modificado en el nuevo archivo
    with open(ruta_archivo_nuevo, 'w', encoding='utf-8') as nuevo_archivo:
        nuevo_archivo.writelines(lineas_procesadas)
    
    return lineas_procesadas
# Ejecutar la función al correr el script
 

if __name__ == "__main__":
    if contar_fits() >= 27:
        ejecutar_consultas()
    else:
        ejecutar_consultas()
        ejecutar_script_bash(f"{route}bash_scripts/comandosCurl_modificado.sh")
        archivo_original = f"{route}bash_scripts/comandosCurl"           # Archivo original
        archivo_nuevo = f"{route}bash_scripts/comandosCurl_modificado.sh"  # Archivo nuevo a generar
        almacenarScript(archivo_original, archivo_nuevo)
        aplicar_chmod()
        ejecutar_script_bash(f"{route}bash_scripts/comandosCurl_modificado.sh")

