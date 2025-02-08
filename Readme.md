# Proyecto de Fotometría de Imágenes TESS

## Descripción del Código

Este proyecto se encarga de automatizar el procesamiento de imágenes tomadas por TESS. El flujo de trabajo consiste en:
- **Descargar** imágenes (ficheros FITS) mediante comandos `curl` definidos en un archivo de texto.
- **Recortar** cada imagen para enfocar únicamente en una estrella de interés (por ejemplo, Algol), utilizando el script `recortes.py`.
- **Consultar** el catálogo de Gaia (con ayuda de SIMBAD) para obtener objetos circundantes y generar un archivo CSV con dicha información.
- **Realizar fotometría** sobre cada imagen recortada para obtener datos instrumentales y compararlos con el catálogo.

De esta forma se evita la descarga y procesamiento del sector completo, concentrándose solo en las imágenes que contienen la estrella de interés.

## Proceso de Ejecución

1. **Generación del script de descarga y procesamiento:**
   - Se ejecuta `main.py`, que se encarga de coordinar el proceso.
   - Al inicio de cada ejecución se borra el progreso anterior (por ejemplo, se limpia la carpeta de imágenes) mediante un script de limpieza.
   - Se consulta el catálogo de Gaia a través de SIMBAD para obtener los objetos circundantes a la estrella de interés.
   - La estrella de interés está definida en el script `recortes.py`.

2. **Procesamiento de las imágenes:**
   - Para cada imagen descargada, si las coordenadas de la estrella coinciden con la imagen, se genera un recorte.
   - Los recortes se guardan en la carpeta `imagenes_cortadas` (o `imagenes_guardadas`, según la configuración) y se elimina la imagen original.
   - Se implementa una comprobación de progreso en el script de Bash que descarga y procesa las imágenes: a medida que se generan recortes, se muestra el progreso (por ejemplo, "Progress: 1/5 images downloaded").  
   - Una vez alcanzado el límite de recortes definidos, el script de Bash se detiene y se continúa con la siguiente fase.

3. **Consulta al Catálogo Gaia:**
   - Se consulta el catálogo Gaia (gaiadr3) para obtener los objetos en un radio de 10 arcmin alrededor de la estrella de interés.
   - Los datos obtenidos se almacenan en un archivo CSV que contiene la información de los objetos circundantes.

4. **Fotometría y Análisis:**
   - Con los recortes de imágenes y el catálogo generado, se ejecuta `phot.py`, el cual realiza la fotometría de cada imagen recortada.
   - Para cada imagen se genera un CSV con los "match" entre los objetos detectados en la imagen y los del catálogo Gaia.

## Requisitos Previos

- **Archivo de Comandos:**  
  Es necesario contar con el archivo `comandosCurl` que contiene los comandos necesarios para descargar las imágenes del sector.  
  Se puede acceder a los datos desde:  
  [TESS Bulk Downloads](https://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html)

- **Acceso a Internet:**  
  El proyecto requiere acceso a internet para conectarse a la API de TESS y a SIMBAD/Gaia.

## Dependencias Necesarias

- [**astrocut**](https://github.com/astrolabsoftware/astrocut)
- [**astropy**](https://www.astropy.org/)  
- Además se utilizan las librerías estándar de Python: `os`, `glob`, `shutil`, `subprocess` y `pandas` (para la gestión de CSV y DataFrames).

## Descripción de los Scripts

1. **consultas.py:**  
   Realiza una consulta al catálogo Gaia (gaiadr3) para obtener los objetos circundantes a la estrella definida (dentro de un radio de 10 arcmin) y guarda los resultados en un archivo CSV.

2. **recortes.py:**  
   Recorre el directorio local en busca de imágenes FITS. Para cada imagen, si las coordenadas de la estrella de interés coinciden, genera un recorte enfocado en esa estrella, lo guarda en un directorio específico y borra la imagen original.

3. **comandosCurl (y su versión modificada comandosCurl_modificado.sh):**  
   Contiene los comandos `curl` necesarios para descargar cada imagen del sector.  
   La versión modificada de este script (generada automáticamente por `almacenarScript`) incluye además:
   - Una llamada única al script de limpieza (`limpieza.sh`).
   - Un bloque de progreso que muestra en la terminal cuántas imágenes recortadas se han generado (por ejemplo, "Progress: 2/5 images downloaded").
   - Una verificación que, al alcanzar el límite definido, detiene la ejecución del script de Bash y permite que el flujo en `main.py` continúe para ejecutar la fotometría.

4. **limpieza.sh:**  
   Este script elimina todos los archivos con extensiones `.csv`, `.fits` y `.fits.out` en el directorio principal.  
   La ruta configurada es `./bash_scripts/limpieza.sh` y se ejecuta solo una vez al inicio del proceso de descargas.

## Ejecución del Proyecto

Para iniciar el proceso, ejecuta:

```bash
python3 main.py
