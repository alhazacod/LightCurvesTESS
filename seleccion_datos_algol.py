import pandas as pd
from astroquery.simbad import Simbad 
from astropy.coordinates import SkyCoord
import astropy.units as u

# Asegurarse de que se agreguen los campos votables deseados (opcional)
Simbad.add_votable_fields('ids')

def identificarEstrella(df, name): 
    """
    La función identificarEstrella recibe un DataFrame con los datos de fotometría
    y el nombre de la estrella a buscar. Consulta SIMBAD para obtener el identificador
    de la estrella y luego filtra el DataFrame para devolver solo las filas donde la columna "ID"
    coincida con dicho identificador.
    
    Parámetros:
      df (DataFrame): Datos leídos del CSV (se espera que contenga una columna "ID").
      name (str): Nombre de la estrella (por ejemplo, "algol").
      
    Retorna:
      DataFrame filtrado con solo las filas pertenecientes a la estrella.
    """
    # Consultar SIMBAD
    result = Simbad.query_object(name)
    if result is None:
        print(f"No se encontró el objeto {name} en SIMBAD.")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
    
    # Intentamos obtener el identificador de la estrella:
    if "IDS" in result.colnames:
        star_id = result["IDS"][0]
    elif "MAIN_ID" in result.colnames:
        star_id = result["MAIN_ID"][0]
    else:
        # Si ninguna de las columnas está presente, se usa el nombre como fallback
        star_id = name

    print(f"Identificador obtenido para {name}: {star_id}")
    
    # Filtrar el DataFrame para conservar solo las filas donde la columna "ID" coincide con star_id
    df_filtrado = df[df["ID"] == star_id]
    return df_filtrado
