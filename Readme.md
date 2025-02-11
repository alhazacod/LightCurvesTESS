# Proyecto de Fotometría de Imágenes TESS

## Descripción del Código

Este proyecto se encarga de automatizar el procesamiento de imágenes tomadas por TESS. El flujo de trabajo consiste en(es decir solo es necesario definir variables y ejecutar main.py):
- **Descargar** imágenes (ficheros FITS) mediante comandos `curl` definidos en un archivo de texto.
- **Recortar** cada imagen para enfocar únicamente en una estrella de interés (por ejemplo, Algol), utilizando el script `recortes.py`.
- **Consultar** el catálogo de Gaia (con ayuda de SIMBAD) para obtener objetos circundantes y generar un archivo CSV con dicha información.
- **Realizar fotometría** sobre cada imagen recortada para obtener datos instrumentales y compararlos con el catálogo.
- **Realización Curvas de luz** Con los datos Obtenidos se producen la gráfica para la curva de luz de la estrella en cuestión



## Proceso de Ejecución

1. **Generación del script de descarga y procesamiento:**
   - Se ejecuta `main.py`, que se encarga de coordinar el proceso.
   - Se recomienda definir la variable threshold en archivos.ý que es el numero de imagenes a descargar  
   - Mas adelante se implementaran las demas variables en el json y la creación de la clase estrella, por ahora esa información este por default como algol y threshold como 20
   - Las curvas de luz se generan automáticamente y se guardan
   - Si no se tiene buen internet se recomienda tener un valor bajo de threshold ya que la descarga de cada imagén puede tardar un tiempo considerable

2. **Procesamiento de las imágenes:**
   - Para cada imagén descargada, si las coordenadas de la estrella coinciden con la imagen, se genera un recorte.
   - Los recortes se guardan en la carpeta `imagenes_cortadas` (o `imagenes_guardadas`, según la configuración) y se elimina la imagen original.
   - Se implementa una comprobación de progreso la función actualizar_progreso() a medida que se generan recortes, se muestra el progreso (por ejemplo, "Progress: 1/5 images downloaded") cada vez que se encuentra un match.  
   - Una vez alcanzado el límite de recortes definidos, el programa  continúa con la siguiente fase.
   - Cada vez que se ejecute el programa se leerá desde la última linea que fue un match( que contenía a algol) para no repetir imagenes, si se quiere reiniciar desde el principio cambiar el valor de "start" en el archivo .json

3. **Consulta al Catálogo Gaia:**
   - Se consulta el catálogo Gaia (gaia2edr) para obtener los objetos en un radio de 10 arcmin alrededor de la estrella de interés.
   - Los datos obtenidos se almacenan en un archivo CSV que contiene la información de los objetos circundantes.

4. **Fotometría y Análisis:**
   - Para cada imagen se genera un CSV con los "match" entre los objetos detectados en la imagen y los del catálogo Gaia.
   - Con los recortes de imágenes y el catálogo generado, se ejecuta `rutina_astrometrica()`, la cual realiza la fotometría de cada imagen recortada, produce las tablas y obtiene los datos para crear las imagenes.


## Requisitos Previos

- **Archivo de Comandos:**  
  Es necesario contar con el archivo `comandosCurl` que contiene los comandos necesarios para descargar las imágenes del sector.  
  Se puede acceder a los datos desde:  
  [TESS Bulk Downloads](https://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html)

- **Acceso a Internet:**  
  El proyecto requiere acceso a internet para conectarse a la API de TESS y a SIMBAD/Gaia.

## Dependencias Necesarias

- [**astrocut**](https://astrocut.readthedocs.io/en/latest/astrocut/index.html)
- [**astropy**](https://www.astropy.org/)  
- [**seaborn**](https://seaborn.pydata.org/)
- [**numpy**](https://numpy.org/)
- [**matplotlib**](https://matplotlib.org/)
- [**photutils**](https://photutils.readthedocs.io/en/stable/)
-se puede editar la linea de seaborn para dejarlo en matplotlib
- Además se utilizan las librerías estándar de Python: `os`, `glob`, `shutil`, `subprocess` y `pandas` (para la gestión de CSV y DataFrames).

## Descripción de los Scripts

1. **main.py:**  
  Contiene la ejecución de los comandos principales
2. **astrometria.py:**  
   Contiene todas las funciones relacionadas a astrometría

3. **archivos.py**  
   -Contiene algunas funciones relacionadas al manejo de archivos 

4. **limpieza.sh:**  
   Este script .sh elimina todos los archivos con extensiones `.csv`, `.fits` y `.fits.out` en el directorio principal.  
   La ruta configurada es `./bash_scripts/limpieza.sh` y es usado para mantener limpio el codigo,es probable que se deba ejecutar el comand chmod para darle acceso como .sh , se ejecuta usando `./limpieza.sh` en la cmd desde el directorio donde se encuentra.

## Ejecución del Proyecto

Para iniciar el proceso, ejecuta:

```bash
python3 main.py
