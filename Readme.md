

---

 <h1>Descripción del Código</h1>
Este código recorta, una por una, las imágenes tomadas por TESS, enfocándolas en una estrella específica (si se encuentra una coincidencia) definida por sus coordenadas de  RA y  DE, evitando así la descarga del sector completo.

<h2>Proceso de Ejecución</h2>
  
  1. ## Generación del script de descarga y procesamiento:
     - Se ejecuta el código `comandos.py`,
     -  Dependiendo si la canitdad de imagenes recortadas ya es mayor o igual que 27 (un sector) se ejecutan los GET request si no se cumple la condición segenera un script de Bash que automatiza la descarga de cada imagen y ejecuta el código para recortarla y eliminar la imagen original.  
     - Se ejecuta la busqueda del catalogo de gaia3
     - La estrella de interés está definida en `recortes.py`.  

  2. ## Procesamiento de las imágenes:
     - Si las coordenadas de la estrella coinciden con una imagen descargada, se genera un recorte y se guarda en la carpeta `imagenes_guardadas`.  
     - Este proceso se repite hasta que todas las imágenes del sector hayan sido procesadas.  

 3. ## Catalogo Gaia:
     - Se hace un llamadao al catalogo de gaia3 con simbad con ayuda del codigo de un compañero, el csv se guarda según un radio en arcominutos encontrando objetos circundantes. 
  

 4. ## Requisitos previos:
     - Solo es necesario contar con el archivo de texto `comandosCurl`, el cual contiene los comandos necesarios para descargar el sector.  
     - El resto del código se ejecutará automáticamente sin intervención adicional.  Se puede acceder a este en: https://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html 
     
 5. ## Dependencias necesarias:
     - Se deben instalar las librerías **astrocut** y astropy.  
     - También se utilizan las librerías **shutil, glob, os y subprocess**, principalmente para ejecutar scripts de **Bash** desde Python y para la gestión de archivos.  

---
6. ## Explicación de los diferentes scripts:
   1.consultas.py Genera una consulta al catalogo de gaia3edr para saber que objetos circundantes hay alrededor de una estrella definida en un radio de 10 arcmin luego guarda los datos en un archivo.csv
   2.recortes.py Realiza un recorte a cualquier imagén .fits que encuentre dentro del directorio local, guardando la imagén recortada en un directorio especifico y borrando la imagén original.
   3.consultas.py Ejecuta los comandos de curl para descargar cada imagén del sector escogido, además modifica el archivo.sh incluyendo la ejecución de recortes.py justo después de cada descarga automatizando el proceso de descarga sin necesidad de descargar todas las imagenes del sector.

### **Importante**
     1. Este proyecto fue desarrollado en WSL y no en un entorno nativo de Linux.  
     2. Para que funcione correctamente, es imprescindible contar con acceso a internet**, ya que se accede a la API de TESS para la descarga de cada imagen.  
     3.  El código no muestra avances en la terminal , pero las imágenes procesadas pueden verse en los directorios correspondientes a medida que son generadas.  

---

### **Posibles Mejoras**
     1. Se puede implementar una solicitud **GET** automatizada que itere sobre un rango de fechas específicas, ya que estas son las variables utilizadas para definir el sector.  Si esto no es posible se puede  realizar un web scrapper que descargue el archivo ffic.sh del sector deseado
     2. Se podría añadir una **barra de progreso en la terminal** o incluso una **interfaz gráfica** para visualizar el proceso en tiempo real.  
     3. Se puede modularizar el codigo creando paquetes, de esa manera se pueden tener solo un cumulo de librerias importadas y omitir repeticiones de codigo en los 3 scripts de fotometría y el movimiento de archivos a otras carpetas-
     4.Se podrían mover todos los scripts secundarios a una carpeta llamada python_scripts cambiando las rutas para que sea mas organizado pero hay que tener mucho cuidado con todos los PATH ya que generan muchos problemas a la hora de realizar movimientos entre carpetas.
---

## Comandos Útiles
- ### Eliminar múltiples archivos de una misma extensión:**
  ```bash
  find . -name '*.fits' -delete
  ```
- ### Hacer ejecutable un script `.sh` 
  *(Esto ya se realiza automáticamente en el código, pero si es necesario manualmente, puedes usar el siguiente comando:)*  
  ```bash
  chmod +x comandosCurl.sh
  ```

---


