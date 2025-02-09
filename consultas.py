
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astropy.coordinates import Angle
import astropy.units as u
import pandas as pd
import shutil
import os

route = "./"
Gaia.ROW_LIMIT = -1 # unlimited -1 or limited 1000...




def query_gaia(coords, radius_arcmin=10):

    """
    Consulta Gaia para obtener los objetos alrededor de las coordenadas dadas.
    Convierte el radio de arcominutos a grados.
    """
    # Convertir radio de arcominutos a grados
    radius_deg = radius_arcmin / 60.0  # Conversión: 1 arcmin = 1/60 grados

    try:
        # Realizar la consulta en Gaia
        job = Gaia.launch_job_async(f"""
            SELECT  ra, dec, source_id
            FROM gaiadr2.gaia_source
            WHERE CONTAINS(POINT('ICRS', ra, dec), 
                           CIRCLE('ICRS', {coords['recta ascencion']}, {coords['declinacion']}, {radius_deg})) = 1
        """)
        results = job.get_results()
     
        return results
    except Exception as e:
        print("Error en la consulta:", e)
        return None

def get_coordinates_from_name(name):
    """
    Obtiene las coordenadas RA y DEC de un objeto por su nombre usando Simbad, 
    e imprime también el ID de la estrella.
    
    Parámetros:
      name (str): Nombre del objeto (por ejemplo, "algol").
    
    Retorna:
      dict: Diccionario con las claves 'recta ascencion', 'declinacion', 'ra_hms', 'dec_dms' y 'id'.
    """
    # Agregar el campo votable para obtener identificadores
    Simbad.add_votable_fields('ids')
    
    result = Simbad.query_object(name)
    if result is None:
        print(f"No se encontró el objeto {name} en SIMBAD.")
        return None

    ra = result['ra'][0]     # RA en formato sexagesimal (ej.: "03 08 10.1324535")
    dec = result['dec'][0]   # DEC en formato sexagesimal (ej.: "+40 57 20.328013")
    
    # Convertir a los formatos deseados
    ra_hms = Angle(ra, unit=u.deg).to_string(unit=u.hourangle, sep=':', precision=7)
    dec_dms = Angle(dec, unit=u.deg).to_string(unit=u.deg, sep=':', precision=6, alwayssign=True)
    
    # Intentamos obtener el identificador:
    # Si la columna 'IDS' existe y contiene datos, se usa; en caso contrario, se usa 'MAIN_ID'
    if "IDS" in result.colnames and result["IDS"][0].strip() != "":
        star_id = result["IDS"][0]
    elif "MAIN_ID" in result.colnames:
        star_id = result["MAIN_ID"][0]
    else:
        star_id = "No disponible"
        
    print(f"ID de la estrella {name}: {star_id}")
    
    coordinates = {
        'recta ascencion': ra,
        'declinacion': dec,
        'ra_hms': ra_hms,
        'dec_dms': dec_dms,
        'id': star_id
    }
    return coordinates
def save_to_csv():
    coordinates = get_coordinates_from_name("algol")
    print(f"las coordenadas de algol son {coordinates}")
    queryResult = query_gaia(coordinates)  
    data = queryResult.to_pandas()
    data.to_csv('datos_gaia3edr.csv',index = False, header=False,sep=" ")
    rows, columns = data.shape
    print(f"Numero de filas: {rows}, Numero de columnas: {columns}")
    move_csv()
def move_csv():
    source_file = "datos_gaia3edr.csv"
    destination_dir = route +"datos_astrometria_modificados"
        # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    # Construct the full destination path for the CSV file
    destination_file = os.path.join(destination_dir, os.path.basename(source_file))
    # Move the file from the source to the destination
    try:
        shutil.move(source_file, destination_file)
        print(f"File '{source_file}' has been moved to '{destination_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    coords = get_coordinates_from_name("algol")
    print("Las coordenadas de algol son:", coords)


save_to_csv()
# Define the source CSV file and destination directory


