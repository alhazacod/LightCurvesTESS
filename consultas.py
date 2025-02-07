
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astropy.coordinates import Angle
import astropy.units as u
import pandas as pd
import os

Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"  # Se utiliza la tercera distribución de gaia 
Gaia.ROW_LIMIT = -1 # unlimited -1 or limited 1000...

def get_coordinates_from_name(name):
    """
    Obtiene las coordenadas RA y DEC de un objeto por su nombre usando Simbad.
    """
    result = Simbad.query_object(name)
    ra = result['ra'][0]  # RA en formato horas y minutos
    dec = result['dec'][0]  # DEC en grados
    ra_hms = Angle(ra, unit=u.deg).to_string(unit=u.hourangle, sep=':', precision=7)
    dec_dms = Angle(dec, unit=u.deg).to_string(unit=u.deg, sep=':', precision=6, alwayssign=True)
    coordinates = {'recta ascencion':ra,'declinacion':dec,'ra_hms':ra_hms,'dec_dms':dec_dms} #diccionario conteniendolo todo 
    return(coordinates)
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
            SELECT source_id, ra, dec
            FROM gaiadr3.gaia_source
            WHERE CONTAINS(POINT('ICRS', ra, dec), 
                           CIRCLE('ICRS', {coords['recta ascencion']}, {coords['declinacion']}, {radius_deg})) = 1
        """)
        results = job.get_results()
     
        return results
    except Exception as e:
        print("Error en la consulta:", e)
        return None


def save_to_csv():
    coordinates = get_coordinates_from_name("algol")
    print(f"las coordenadas de algol son {coordinates}")
    queryResult = query_gaia(coordinates)  
    data = queryResult.to_pandas()
    data.to_csv('datos_gaia3edr.csv',index = False)
    rows, columns = data.shape
    print(f"Numero de filas: {rows}, Numero de columnas: {columns}")
  
save_to_csv()
