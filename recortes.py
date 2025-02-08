import os
import glob
import shutil
from astrocut import fits_cut
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astrocut.exceptions import InvalidQueryError
import uuid  # For generating unique filenames

route = "./"

def cortarImagen(name):
    # Find all FITS files in the current directory
    fits_files = glob.glob(route+"*.fits")
    if not fits_files:
        print("No se ha encontrado ninguna imagen FITS")
        return None

    input_file = fits_files[0]

    # Query SIMBAD for the object
    result = Simbad.query_object(name)
    if result is None:
        print(f"No se encontró el objeto {name} en SIMBAD")
        return None

    # Extract RA and DEC from the result
    ra = result['ra'][0]    # RA in hours/minutes/seconds format (or degrees, depending on SIMBAD's output)
    dec = result['dec'][0]  # DEC in degrees

    # Use an f-string so that the variables are interpolated into the string.
    center_coord = SkyCoord(f"{ra} {dec}", unit="deg")
    cutout_size = [1000, 1000]

    try:
        # Perform the cutout using fits_cut
        cutout_file = fits_cut(input_file, center_coord, cutout_size, single_outfile=True)
    except InvalidQueryError:
        os.remove(input_file)
        return None
    except Exception as e:
        print("Error inesperado durante el recorte:", e)
        return None

    print("Se encontró un match, realizando recorte")
    
    # Create the destination directory if it doesn't exist
    dest_dir = route+"imagenes_cortadas"
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # Convert the cutout file and destination directory paths to absolute paths
    cutout_file_abs = os.path.abspath(cutout_file)
    dest_dir_abs = os.path.abspath(dest_dir)

    # Generate a unique filename for the recut file
    unique_filename = f"cutout_{uuid.uuid4().hex}.fits"
    dest_file = os.path.join(dest_dir_abs, unique_filename)

    # Move the cutout file to the destination directory
    shutil.move(cutout_file_abs, dest_file)

    # Remove the original input file
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