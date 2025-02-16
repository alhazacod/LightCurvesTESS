# Proyecto de Fotometría de Imágenes TESS

## Descripción del Código

Este proyecto automatiza el procesamiento de imágenes tomadas por TESS. El flujo de trabajo se centra en definir variables y ejecutar `main.py`, el cual coordina todo el proceso. Las principales tareas del proyecto son:

- **Descargar** imágenes (archivos FITS) mediante comandos `curl` definidos en un archivo de texto.
- **Recortar** cada imagen para enfocar únicamente en una estrella de interés (por ejemplo, Algol), utilizando el script `recortes.py`.
- **Consultar** el catálogo de Gaia (con ayuda de SIMBAD) para obtener objetos circundantes y generar un archivo CSV con dicha información.
- **Realizar fotometría** en cada imagen recortada para extraer datos instrumentales y compararlos con el catálogo.
- **Generar Curvas de Luz:** Con los datos obtenidos se produce la gráfica de la curva de luz de la estrella en cuestión.

## Proceso de Ejecución

1. **Generación del script de descarga y procesamiento:**
   - Se ejecuta `main.py`, que coordina el proceso.
   - Se recomienda definir la variable `threshold` en el archivo de rutas, la cual indica el número de imágenes a descargar.
   - Por ahora, la información se establece por defecto: la estrella es "algol" y el `threshold` es 20.
   - Las curvas de luz se generan automáticamente y se guardan.
   - Si la conexión a Internet es lenta, se recomienda usar un `threshold` menor, ya que la descarga de cada imagen puede demorar.

2. **Procesamiento de las imágenes:**
   - Cada imagen descargada se verifica para ver si contiene la estrella de interés; si es así, se genera un recorte.
   - Los recortes se guardan en la carpeta `imagenes_cortadas` (o `imagenes_guardadas`, según la configuración) y se elimina la imagen original.
   - La función `actualizar_progreso()` se invoca cada vez que se encuentra un match, mostrando mensajes de progreso (por ejemplo, "Progress: 1/5 images downloaded").
   - Una vez alcanzado el límite de recortes definidos, el programa continúa con la siguiente fase.
   - Cada vez que se ejecuta el programa, se lee desde la última línea que produjo un match (la línea se guarda en un archivo JSON). Para reiniciar la ejecución desde el principio, se debe cambiar el valor de `"start"` en el archivo `info.json`.

3. **Consulta al Catálogo Gaia:**
   - Se consulta el catálogo Gaia (gaia2edr) para obtener objetos en un radio de 10 arcmin alrededor de la estrella de interés.
   - Los datos obtenidos se almacenan en un archivo CSV que contiene la información de los objetos circundantes.

4. **Fotometría y Análisis:**
   - Para cada imagen se genera un CSV con los “match” entre los objetos detectados y los del catálogo Gaia.
   - Con los recortes y el catálogo generado se ejecuta `rutina_astrometrica()`, la cual realiza la fotometría de cada imagen recortada, produce las tablas y extrae los datos para generar las curvas de luz.
   - Los archivos resultantes se organizan en diferentes carpetas:
     - `imagenes_cortadas`: imágenes recortadas que contienen Algol.
     - `datos_astrometria_modificados`: archivos CSV con datos fotométricos.
     - `fits_out`: archivos `.fits.out` generados por la fotometría.

## Requisitos Previos

- **Archivo de Comandos:**  
  Se requiere contar con el archivo `comandosCurl` que contiene los comandos `curl` necesarios para descargar las imágenes del sector.  
  Accede a los datos desde:  
  [TESS Bulk Downloads](https://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html)

- **Acceso a Internet:**  
  El proyecto requiere conexión a internet para conectarse a la API de TESS y a los catálogos SIMBAD/Gaia.

## Dependencias Necesarias

- [**astrocut**](https://astrocut.readthedocs.io/en/latest/astrocut/index.html)
- [**astropy**](https://www.astropy.org/)
- [**seaborn**](https://seaborn.pydata.org/) *(o matplotlib, según preferencia)*
- [**numpy**](https://numpy.org/)
- [**matplotlib**](https://matplotlib.org/)
- [**photutils**](https://photutils.readthedocs.io/en/stable/)
- [**rich**](https://rich.readthedocs.io/) *(para la visualización avanzada en terminal)*
- **Librerías estándar de Python:** `os`, `glob`, `shutil`, `subprocess`, `pandas`, `csv`

## Descripción de los Scripts

1. **main.py:**  
   Contiene la ejecución de los comandos principales.  
   - Lee el archivo JSON para retomar desde la última línea procesada.  
   - Ejecuta el script modificado de descarga, que incluye comprobaciones de progreso y actualizaciones de la variable `"start"`.
   - Finalmente, llama a la función de fotometría.

2. **astrometria.py:**  
   Contiene todas las funciones relacionadas con la astrometría y el procesamiento de imágenes, incluyendo:
   - Recorte de imágenes (`recortes.py`).
   - Consultas a SIMBAD y Gaia.
   - Generación de tablas de fotometría y curvas de luz.

3. **archivos.py:**  
   Contiene funciones para el manejo y movimiento de archivos entre directorios.

4. **limpieza.sh:**  
   Script de shell que elimina archivos con extensiones `.csv`, `.fits` y `.fits.out` en el directorio principal para mantener el proyecto limpio.  
   - Se recomienda ejecutar `chmod +x bash_scripts/limpieza.sh` para otorgar permisos de ejecución.

5. **Otros archivos en `all_scripts`:**  
   - **todas_las_rutas.py:** Define todas las rutas del programa.
   - **archivos.py:** Funciones enfocadas a la modificación y movimiento de archivos.
   - **astrometria.py:** Funciones relacionadas con el análisis de imágenes y fotometría.

## Ejecución del Proyecto

Antes de iniciar el proceso principal, se recomienda ejecutar el script `instalacion_librerias.sh` para instalar todas las dependencias.

Para iniciar el proceso, ejecuta:

```bash
python3 main.py

