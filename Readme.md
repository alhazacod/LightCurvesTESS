

---

 <h1>Descripción del Código</h1>
Este código recorta, una por una, las imágenes tomadas por TESS, enfocándolas en una estrella específica (si se encuentra una coincidencia) definida por sus coordenadas de **RA** y **DE**, evitando así la descarga del sector completo.

<h2>Proceso de Ejecución</h2>
  1. ## Generación del script de descarga y procesamiento:
     - Se ejecuta el código `comandos.py`,
     -  el cual genera un script de **Bash** que automatiza la descarga de cada imagen y ejecuta el código para recortarla y eliminar la imagen original.  
     - La estrella de interés está definida en `recortes.py`.  

  2. ## Procesamiento de las imágenes:
     - Si las coordenadas de la estrella coinciden con una imagen descargada, se genera un recorte y se guarda en la carpeta `imagenes_guardadas`.  
     - Este proceso se repite hasta que todas las imágenes del sector hayan sido procesadas.  

 3. ## Requisitos previos:
     - Solo es necesario contar con el archivo de texto **`comandosCurl`**, el cual contiene los comandos necesarios para descargar el sector.  
     - El resto del código se ejecutará automáticamente sin intervención adicional.  Se puede acceder a este en: https://archive.stsci.edu/tess/bulk_downloads/bulk_downloads_ffi-tp-lc-dv.html

 4. ## Dependencias necesarias:
     - Se deben instalar las librerías **astrocut** y **astropy**.  
     - También se utilizan las librerías **shutil, glob, os y subprocess**, principalmente para ejecutar scripts de **Bash** desde Python y para la gestión de archivos.  

---

### **Importante**
     - Este proyecto fue desarrollado en **WSL** y no en un entorno nativo de **Linux**.  
     - Para que funcione correctamente, es **imprescindible contar con acceso a internet**, ya que se accede a la **API de TESS** para la descarga de cada imagen.  
     - ** El código no muestra avances en la terminal **, pero las imágenes procesadas pueden verse en los directorios correspondientes a medida que son generadas.  

---

### **Posibles Mejoras**
     - Se puede implementar una solicitud **GET** automatizada que itere sobre un rango de fechas específicas, ya que estas son las variables utilizadas para definir el sector.  Si esto no es posible se puede  realizar un web scrapper que descargue el archivo ffic.sh del sector deseado
     - Se podría añadir una **barra de progreso en la terminal** o incluso una **interfaz gráfica** para visualizar el proceso en tiempo real.  

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

Este texto mantiene la esencia de tu explicación, pero con una mejor estructura, corrección ortográfica y mayor claridad. ¡Déjame saber si necesitas algún ajuste! 🚀
