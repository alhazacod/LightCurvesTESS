import os
import glob
import shutil
from astrocut import fits_cut
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astrocut.exceptions import InvalidQueryError

route = "./"

def cortarImagen(name):
    # Buscar todos los archivos FITS en el directorio actual
    fits_files = glob.glob(route + "*.fits")
    if not fits_files:
        print("No se ha encontrado ninguna imagen FITS")
        return None

    input_file = fits_files[0]

    # Consulta a SIMBAD para el objeto
    result = Simbad.query_object(name)
    if result is None:
        print(f"No se encontró el objeto {name} en SIMBAD")
        return None

    # Extraer RA y DEC de la consulta (en formato sexagesimal)
    ra = result['ra'][0]    # RA en horas/minutos/segundos (o grados, según la salida de SIMBAD)
    dec = result['dec'][0]  # DEC en grados

    # Convertir la cadena a coordenadas usando SkyCoord
    center_coord = SkyCoord(f"{ra} {dec}", unit="deg")
    cutout_size = [1000, 1000]

    try:
        # Realizar el recorte utilizando fits_cut
        cutout_file = fits_cut(input_file, center_coord, cutout_size, single_outfile=True)
    except InvalidQueryError:
        os.remove(input_file)
        return None
    except Exception as e:
        print("Error inesperado durante el recorte:", e)
        return None

    print("Se encontró un match, realizando recorte")
    
    # Crear el directorio de destino si no existe
    dest_dir = route + "imagenes_cortadas"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Convertir las rutas a absolutas
    cutout_file_abs = os.path.abspath(cutout_file)
    dest_dir_abs = os.path.abspath(dest_dir)

    # Generar un nombre secuencial para el archivo recortado
    # Se cuenta el número de archivos .fits ya presentes y se suma 1
    count = len(glob.glob(os.path.join(dest_dir_abs, "*.fits"))) + 1
    unique_filename = f"{count}_{name}.fits"
    dest_file = os.path.join(dest_dir_abs, unique_filename)

    # Mover el archivo recortado al directorio de destino
    shutil.move(cutout_file_abs, dest_file)

    # Borrar el archivo original utilizado para el recorte
    try:
        os.remove(input_file)
    except OSError as e:
        print(f"Error al borrar el archivo original {input_file}: {e}")

    print(f"Imagen recortada guardada en: {dest_file}")
    return dest_file

def borrarImagen(file_path):
    """
    Borra el archivo FITS indicado por file_path.
    
    Parámetros:
        file_path (str): Ruta del archivo a borrar.
    """
    try:
        os.remove(file_path)
        print(f"Imagen {file_path} borrada exitosamente.")
    except OSError as e:
        print(f"Error al borrar la imagen {file_path}: {e}")

# Ejemplo de uso:
if __name__ == "__main__":
    name = "algol"
    cortarImagen(name)
