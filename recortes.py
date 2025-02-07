import os
import glob
import shutil
from astrocut import fits_cut
from astropy.coordinates import SkyCoord
from astrocut.exceptions import InvalidQueryError

import uuid  # For generating unique filenames

def cortarImagen():
    fits_files = glob.glob("./*.fits")
    if not fits_files:
        print("No se ha encontrado ninguna imagen FITS")
        return None

    input_file = fits_files[0]

    center_coord = SkyCoord("47.0422185563 40.9556466703", unit="deg")
    cutout_size = [100, 100]

    try:
        cutout_file = fits_cut(input_file, center_coord, cutout_size, single_outfile=True)
    except InvalidQueryError:
        os.remove(input_file)
        return None
    except Exception as e:
        print("Error inesperado durante el recorte:", e)
        return None

    print("Se encontró un match, realizando recorte")
    
    dest_dir = "./imagenes_cortadas"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    cutout_file_abs = os.path.abspath(cutout_file)
    dest_dir_abs = os.path.abspath(dest_dir)

    # Generate a unique filename using a UUID
    unique_filename = f"cutout_{uuid.uuid4().hex}.fits"
    dest_file = os.path.join(dest_dir_abs, unique_filename)

    shutil.move(cutout_file_abs, dest_file)

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
   cortarImagen()

