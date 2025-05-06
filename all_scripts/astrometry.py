# -*- coding: utf-8 -*-
###################################################################
# Fotometria de imégenes IRAC/SPITZER                             #
# Giovanni Pinzon, Andres Felipe Caro
###################################################################

# Librerias
# **photutlis 1.3.0** ; **astropy 4.3.1** 

# INPUT : (1) Directorio en donde se encuentran las imagenes, calibradas
#             astrom�tricamente lin(28)
#             (https://nova.astrometry.net/upload)
#         (2) Cat�logo RA DEC ID "catgaia" lin(52) 
#         (3) Ruta Archivos de Salida *csv conteniendo la fotometr�a lin (343) 
#         (4) Par�metros fotom�tricos lin(256-58)

# OUTPUT : Archivos de texto plano *csv 
#          Algol_{foc}.csv


#Imports #
from photutils.centroids import centroid_sources, centroid_com
from photutils.aperture import CircularAperture
from photutils.aperture import CircularAnnulus
from photutils.aperture import aperture_photometry
from photutils.utils import calc_total_error
from scipy.signal import periodogram
from scipy.stats import mode
from astrocut.exceptions import InvalidQueryError
from astroquery.simbad import Simbad
from astrocut import fits_cut
from astroquery.gaia import Gaia
from astroquery.simbad import Simbad
from astropy.coordinates import Angle
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table
from astropy.table.table import QTable
from astropy.coordinates import SkyCoord
from astropy.stats import sigma_clipped_stats
from astropy.timeseries import LombScargle
from phoebe import u
from astropy.time import Time
from astropy import units as u
from datetime import datetime
from rich.progress import Progress
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from all_scripts import files
from all_scripts import all_paths as paths
import pandas as pd
import numpy as np
import os
import csv
import subprocess
import glob
import shutil
import time
import phoebe

class Star:
    def __init__(self, name_estrella, threshold):
        self._name_estrella = name_estrella
        self._threshold = threshold

    @property
    def name_estrella(self):
        return self._name_estrella

    @name_estrella.setter
    def name_estrella(self, value):
        self._name_estrella = value

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = value


# Fotometría de apertura usando Photutils + Objetos de catálogo

#variables globales
# Directorios definidos en archivos.py
#carpeta = arch.imagenes_cortadas
center_box_size=3  
#star = Star("algol",arch.threshold)
Simbad.add_votable_fields('ids')
Simbad.add_votable_fields('ids')

#Funciones que realizan cada una de las tareas
def save_to_csv(rutas,estrella):
    coordinates = get_coordinates_from_name(estrella)
    print(f"las coordenadas de {estrella} son {coordinates}")
    queryResult = query_gaia(coordinates)  
    data = queryResult.to_pandas()
    nombre_archivo = f'{estrella}_datos_gaiaedr.csv'
    directorio = rutas['archivo_catalogo']
    data.to_csv(nombre_archivo,index = False, header=False,sep=" ")
    rows, columns = data.shape
    print(f"Numero de filas: {rows}, Numero de columnas: {columns}")
    files.mover_objeto(nombre_archivo,directorio,rutas)
#Se define la función que toma las coordenadas y hace el query en gaia
def query_gaia(coordinates, radius_arcmin=1):
    ra = coordinates['recta ascencion']   # RA en horas/minutos/segundos (o grados, según la salida de SIMBAD)
    dec = coordinates['declinacion'] 
    radius_deg = radius_arcmin / 60.0  # Conversión: 1 arcmin = 1/60 grados
    try:
        # Realizar la consulta en Gaia
        job = Gaia.launch_job_async(f"""
            SELECT  ra, dec,source_id
            FROM gaiadr2.gaia_source
            WHERE CONTAINS(POINT('ICRS', ra, dec), 
                           CIRCLE('ICRS', {ra}, {dec}, {radius_deg})) = 1
        """)
        results = job.get_results()
        return results
    except Exception as e:
        print("Error en la consulta:", e)
        return None
#Obtener el ID de gaia
def gaia_ids(estrella):
    Simbad.add_votable_fields("ids")
    result = Simbad.query_object(estrella)
    if result is not None and len(result) > 0 :
        ids = result["ids"][0].split("|")
      
        for id_ in ids:
            if "Gaia DR2" in id_:
                global gaia_id
                gaia_id = int(id_.replace("Gaia DR2 ", ""))
                print(f"🔍 Gaia DR2 ID de {estrella}: {gaia_id}")  
                return True  
                
    else:
        print(f"No se encontró el objeto '{estrella}' en Simbad.")
        return False
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
    try:
      result = Simbad.query_object(name)
    except Exception as e:
        print(f"An error occurred: {e}")
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
def cortarImagen(coordinates, input_file, rutas, estrella):
    """
    Processes a downloaded FITS file by cutting it to focus on the specified star.
    It searches for the input file in rutas['imagenes'] and, after cutting, moves the result
    to rutas['imagenes_cortadas']. Then, the original file is deleted.
    """
    name = estrella
    verdad = True
    if not input_file:
        print("No se ha encontrado ninguna imagen FITS")
        return None  

    # Use the coordinates provided.
    ra = coordinates['recta ascencion']
    dec = coordinates['declinacion']
    center_coord = SkyCoord(f"{ra} {dec}", unit="deg")
    cutout_size = [1000, 1000]

    try:
        # Perform the cutout using fits_cut
        cutout_file = fits_cut(input_file, center_coord, cutout_size, single_outfile=True)
    except InvalidQueryError:
        os.remove(input_file)
        verdad = False
        return verdad
    except Exception as e:
        print("Error inesperado durante el recorte:", e)
        os.remove(input_file)
        verdad = False
        return verdad

    print("Se encontró un match, realizando recorte")
    
    # Use the output directory from rutas for the recut images.
    dest_dir = rutas['imagenes_cortadas']
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    cutout_file_abs = os.path.abspath(cutout_file)
    dest_dir_abs = os.path.abspath(dest_dir)

    # Generate a sequential name based on the number of existing recut files.
    count = len(glob.glob(os.path.join(dest_dir_abs, "*.fits"))) + 1
    unique_filename = f"{count}_{name}.fits"
    dest_file = os.path.join(dest_dir_abs, unique_filename)
    
    shutil.move(cutout_file_abs, dest_file)
    
    try:
        os.remove(input_file)
        print(f"Imagen {input_file} borrada exitosamente.")
    except OSError as e:
        print(f"Error al borrar la imagen {input_file}: {e}")
    
    print(f"Imagen recortada guardada en: {dest_file}")
    return verdad
def is_in_pic(w, image, ra, dec):
    '''
     Funcion que ajusta los objetos del catalogo a solo aquellos que podr�an estar en la im�gen
    '''
    ra_max, dec_max = w.array_index_to_world_values(0,0)
    ra_min, dec_min = w.array_index_to_world_values(image.shape[0], image.shape[1])
    if ra_min > ra_max:
      ra_min = w.array_index_to_world_values(0,0)[0]
      ra_max = w.array_index_to_world_values(image.shape[0], image.shape[1])[0]
    if dec_min > dec_max:
      dec_min = w.array_index_to_world_values(0,0)[1]
      dec_max = w.array_index_to_world_values(image.shape[0], image.shape[1])[1]
      
    return (ra < ra_max) & (ra > ra_min) & (dec < dec_max) & (dec >   dec_min)
def Photometry_Data_Table(rutas,fits_name, fits_path, catalogo, r, r_in, r_out, center_box_size, *args):
  '''
  Esta función se encarga de añadir la información astrometrica de la imagén fits como fits_data
  '''
  # Se abre el archivo .fits para guardarlo como una variable i.e. image / fits_data
  F = fits.open(fits_path)
  FitsData = F
  w = WCS(FitsData[1].header)
  fits_data = FitsData[1].data
  fits_header = FitsData[1].header

  itime  = 1800
  #TSTART observation start time in BTJD  

  target1 = fits_header['TSTART']
  print(target1)
  
  target=fits_header.append(('OBJECT',target1), end=True)  
  print(fits_path)
  
  ifilter = 'TESS'  
  DateObs = fits_header['DATE-OBS']
  
  epadu = 5.22
  F.close()

  image=fits_data


 
  NewListO = open(f"Objectlist_{fits_name}.out", "w")
  # Contador de objetos de cat�logo que est�n en la im�gen
  object_counter = 0
  for j in range(0,len(catalogo)):
    condicion = is_in_pic(w, image, catalogo[j][0],catalogo[j][1])
    if condicion:
      object_counter +=1
      X, Y = SkyCoord(catalogo[j][0], catalogo[j][1], frame="icrs", unit="deg").to_pixel(w)
      NewListO.write(f"{catalogo[j][0]}     {catalogo[j][1]}     {catalogo[j][2]}   {X}   {Y}   {condicion}\n")
  NewListO.close()
  print(f'\n Se han encontrado {object_counter} objetos del catalogo en el archivo .fits \n')

  if object_counter == 0:
    print(f"⚠️ No objects found in {fits_name}, skipping this image.")
    return None


# Se guardan las coordenadas de los objetos de cat�logo que est�n en la im�gen
  nombre_fits_out = f"Objectlist_{fits_name}.out"
  ruta_fits_out =paths.route+nombre_fits_out
  Obj = open(nombre_fits_out, "r")
  ListObj = Obj.readlines()
  Obj.close()
  files.mover_objeto(ruta_fits_out,rutas['fits_out'],rutas)
  Final_LO = []
  for i in ListObj:
    Final_LO.append(i.split()[:5])
  RA, DEC, ID, x, y = zip(*Final_LO) 
  Final_List = np.array(list(zip(RA,DEC,x,y)), dtype=float)
  ID = np.array(ID,dtype='U20')

  # Eliminar los objetos que no esten en el archivo fits (en caso de que la funcion is_in_pic() haya fallado numericamente)
  mm = [ 0 < i[2] and i[2] < (image.shape[0] - 1) for i in Final_List] # Lista de [Booleanos] (x) en las cuales las posiciones si esten en la imagen
  ID = ID[mm]
  Final_List = Final_List[mm]
  nn = [ 0 < i[3] and i[3] < (image.shape[1] - 1) for i in Final_List] # Lista de [Booleanos] (y) en las cuales las posiciones si esten en la imagen
  ID = ID[nn]
  Final_List = Final_List[nn]

# IDs repetidos se categorizan 
  u, c = np.unique(ID, return_counts=True)
  dup = u[c > 1]
  for j in dup:
    m = 0
    for i in range(len(ID)):
      if ID[i] == j:
        m += 0.1
        ID[i] = ID[i] + str(m)

# Se imprime en consola una previsualizacion de como es el nuevo catalogo reducido.
  np.set_printoptions(suppress=True, formatter={'float_kind':'{:f}'    .format})
  print(f"\nSu catalogo reducido es (filas {len(Final_List)}):\n ")
  print("----RA---- ---DEC--- -----x-----  -----y----- -----ID-------\n")
  print(Final_List[0],ID[0])
  print("    ...       ...         ...          ...         ...        \n")
  print(Final_List[len(Final_List)-1],ID[len(Final_List)-1])
  print("---------- --------- ------------  ----------- -------------\n")

# Se extraen los valores X y Y
  _, _, x_init, y_init = zip(*Final_List)




  x, y = centroid_sources(image, x_init, y_init, box_size = center_box_size, centroid_func=centroid_com)
  X, Y = np.array(x), np.array(y)
  NewIDS = np.array(ID) 
    
# Se eliminan los datos a los cuales tienen un centroide NaN o inf
  is_nan = ~np.isnan(X)
  x, y = X[is_nan],Y[is_nan]      
  Final_List2 = Final_List[is_nan] 
  NewIDS = NewIDS[is_nan]

# Centroides de coordenadas de las estrellas 
  starloc = list(zip(x,y))
  if isinstance(starloc, np.ma.MaskedArray):
    starloc = starloc.filled(np.nan)  # Convert masked values to NaN

  if np.isnan(starloc).any() or np.isinf(starloc).any():
    raise ValueError(f"Invalid star location detected: {starloc}")
  if len(starloc) == 0:
    print(f"⚠️ No valid star positions found in {fits_name}, skipping this image.")
    return None
  print(starloc)
  print(starloc, np.isnan(starloc).any(), np.isinf(starloc).any())
  print(f"starloc type: {type(starloc)}, value: {starloc}")
 
  zmag = 20.4402281476
  
    
# Extracci�n se�al de cada estrella
  aperture = CircularAperture(starloc, r=r)
  annulus_aperture = CircularAnnulus(starloc, r_in=r_in, r_out=r_out )
  apers = [aperture, annulus_aperture]
  # Se genera una tabla de datos.
  phot_table = aperture_photometry(image, apers)

  # Se le asigna nombre de la magnitud dependiendo del filtro en el encabezado
  name_mag = str(ifilter)

  # Area y fujo en los anillos. 
  bkg_mean = phot_table['aperture_sum_1'] / annulus_aperture.area
  area_aper = np.array(aperture.area_overlap(image))
  bkg_sum = bkg_mean * area_aper
  print("==============================================================\n")
  
  # Flujo final para cada objeto
  final_sum = phot_table['aperture_sum_0'] - bkg_sum
  phot_table['flux'] = final_sum
  phot_table['flux'].info.format = '%.8g' 
  
  # Magnitudes Instrumentales


  phot_table[name_mag + '_mag'] = zmag - 2.5 * np.log10(abs(final_sum)) 
  phot_table[name_mag + '_mag'].info.format = '%.8g'  
    
  # Error de las Magnitudes Instrumentales

  mean, median, std = sigma_clipped_stats(image, sigma=3.0)
  stdev = std
  phot_table[name_mag + '_mag_err'] = 1.0857 * np.sqrt(abs(final_sum)    /epadu + area_aper*stdev**2 )/abs(final_sum)
  phot_table[name_mag + '_mag_err'].info.format = '%.8g'

  # Se agrega a la tabla la RA, DEC, ID y Masa de aire. 
  phot_table['RA'] = [i[0] for i in Final_List2] 
  phot_table['DEC'] = [i[1] for i in Final_List2] 
  phot_table['ID'] = NewIDS
 # phot_table['AIRMASS'] = airmass
  phot_table['DATE-OBS'] = DateObs
 # phot_table['APERTURE'] = r
 # phot_table['Rint'] = r_in
 # phot_table['Rout'] = r_out
 # phot_table['AIRTEMP'] = ccdtemp
  phot_table['OBJECT'] = fits_header['OBJECT']
  # Se buscan los indices en donde las magnitudes sean NaN y se eliminan
  index_nan = np.argwhere(np.isnan(phot_table[name_mag + '_mag'].data)) 
  phot_table.remove_rows(index_nan)
  filas = len(phot_table)
 
  return phot_table   
def cantidad_de_fits(archive,rutas):
  # Impresion de los archivos encontados y guardado de nombre del archivo en lista
  #print("\n Archivos Encontrados")
  carpeta = rutas['imagenes_cortadas']
  nombres = []
  for j in archive:
    if carpeta in j:
      nombres.append(j.replace(carpeta,'')) 

  if nombres != []:
    l = len(nombres)
    print(f'\n Su carpeta tiene {l} archivos .fits \n')
    print(f'No. 1: {nombres[0]}')
    print(f'          ....            ')
    print(f'No. {l}: {nombres[l-1]}')
  else: 
    print('\n Su carpeta no tiene archivos .fits \n')
  return nombres
  # Carga del cat�logo con coordenadas e identificador :  RA DEC ID
  # !!!!!!! FORMATO DEBE ESTAR EN: RA - DEC - ID   
def lectura_de_catalogo(data):
    """
    Lee el catálogo desde el archivo 'data' y retorna tres listas: ra, dec e id.
    Se ignoran las líneas que no contengan al menos tres elementos.
    
    Parámetros:
        data (str): Ruta del archivo de catálogo.
    
    Retorna:
        tuple: (ra, dec, id) listas con los valores correspondientes.
    """
    with open(data, "r") as catalogo:
        objects = catalogo.readlines()
    
    L_O = []
    for i in objects:
        tokens = i.split()
        # Se agrega la línea solo si tiene al menos 3 elementos (RA, DEC, ID)
        if len(tokens) >= 3:
            L_O.append(tokens)
    
    if not L_O:
        print("No se encontraron entradas válidas en el catálogo.")
        return [], [], []
    
    ra = [i[0] for i in L_O]
    dec = [i[1] for i in L_O]
    id = [i[2] for i in L_O]
    return ra, dec, id
def adicionFiltros(all_tables):
  '''
  Esta función se encarga de crear una lista de los objetos enfocados en la foto del telescopio usando todas las tablas disponibles para la fotometría,luego se encarga de añadir los filtros necesario para cada objeto circundante
  '''
  #----# Crea lista con los nombres de los objetos a los cuales se enfoca el telescopio
  object_of_focus = []             
  for m in all_tables:
    
  #if m != []:
    ob = m['OBJECT'][0]
    
    if ob not in object_of_focus:
      
      object_of_focus.append(ob)   # Ejemplo: focus_object = ['SA98', 'SA95', '[BSA98', 'SA101', '[ASA98', 'SA104', 'SA92']

  #----#  Se crea diccionario con cada objeto de enfoque
  filtro_final = {}
  for s in object_of_focus:
    filtro_final[s] = []        # Ejemplo: filtro_final = {'SA98':[], 'SA95':[], '[BSA98':[], 'SA101':[], '[ASA98':[], 'SA104':[], 'SA92':[]}

  #----#  Se llena el diccionario
  for n in all_tables:
    for p in object_of_focus:
      ob = n['OBJECT'][0]
      if ob == p:
        filtro_final[ob].append(n.copy())
  # Ejemplo: filtro_final = {'SA98':[tabla1,tabla2,tabla3,..], ... , 'SA92':[tabla1,tabla2,tabla3,..]}
  return object_of_focus,filtro_final
def creacionTablasCsv(filtro_final,rutas,estrella):
  '''
  Esta función se encarga de crear todas las tablas .csv que seran usadas para la producción de curvas de luz para algol
  '''
  #----# Se crean tablas para cada objeto de enfoque
  for foc in filtro_final.keys():
    final_obs_table = QTable()
    final_obs_table['OBJECT_ID'] = filtro_final[foc][0]['ID']
    final_obs_table['RA'] = filtro_final[foc][0]['RA']
    final_obs_table['DEC'] = filtro_final[foc][0]['DEC']

  #----# Se guardan las tablas como archivos .csv
    counter = 0
    for j in filtro_final[foc]:
      
    
      final_obs_table[j.colnames[6] + '_' + str(counter//3)] = j[j.colnames[6]]
      final_obs_table[j.colnames[7] + '_' + str(counter//3)] = j[j.colnames[7]]
      final_obs_table[j.colnames[11] + '_' + j.colnames[6] + '_' + str(counter//3)] = j[j.colnames[11]]
      counter += 1
    estrella_csv = f"{estrella}_{foc}.csv"
    estrella_csv_ruta = f"{rutas['csv_out']}{estrella}_{foc}.csv"
    final_obs_table.write(estrella_csv_ruta, overwrite=True) 
    #files.mover_objeto(estrella_csv,rutas['csv_out'])   
def interseccionFiltros(focus_object,filtro_final):
  '''
  Esta función se encarga de realizar la intersección de los objetos que estan en los tres filtros, al terminar elimina los datos por fuera de los tres libros y elimina las tablas vacias pertenecientes a allTables
  '''
  #----#  Para cada observacion de enfoque se hace la interseccion de los objetos que esten en los tres filtros
  for foc in focus_object:
    current_id = []
    for j in filtro_final[foc]:
      current_id.append(j['ID'].data)
    
    int_d = set(current_id[0]).intersection(*current_id) # Ejemplo para SA98: int_d = {'92_248', ... , '92_347'}

    #----# Se eliminan los objetos que no esten en los tres filtros
    for tab in filtro_final[foc]:
      index_of = []
      for i in range(len(tab['ID'])):
        if tab['ID'][i] not in int_d:
          index_of.append(i)
      tab.remove_rows(index_of)

  #----# Eliminar las tablas que esten vacias
  for p in focus_object:
    if len(filtro_final[p][0]) == 0:
      del filtro_final[p]

  for foc in filtro_final.keys():
    let = len(filtro_final[foc])
  return filtro_final
# Module-level helper function (do not nest this inside creacionTablasFotometricas)


def creacionTablasFotometricas(rutas, estrella):
    """
    Esta función crea los datos de todas las fotos que se encuentran en imagenes cortadas,
    realizando la fotometría para todas las imágenes *.fits.
    """

    # Buscar archivos FITS
    archivos = glob.glob(rutas['imagenes_cortadas'] + '*.fits')

    # Definir nombres de los archivos FITS
    nombres = cantidad_de_fits(archivos, rutas)

    # Cargar catálogo de estrellas
    nombre_archivo_csv = f"{estrella}_datos_gaiaedr.csv"
    try:
        ra, dec, id_estrella = lectura_de_catalogo(rutas['archivo_catalogo'] + nombre_archivo_csv)
    except Exception as e:
        print(f"❌ Error al leer el catálogo {nombre_archivo_csv}: {e}")
        return []

    catalogo_decimal = SkyCoord(ra, dec, unit=(u.degree))
    catalogor = list(zip(catalogo_decimal.ra.deg, catalogo_decimal.dec.deg, id_estrella))

    # Definir parámetros fotométricos
    rr = 10      # Apertura en px
    r_inr = 12   # Radio interno anillo cielo
    r_outr = 14  # Radio externo
    all_tables = []
    valor_total = len(archivos)

    # Iterar sobre todas las imágenes FITS
    for k, (fits_pathr, fits_namer) in enumerate(zip(archivos, nombres)):
        subprocess.run("clear", shell=True, check=True, text=True)
        print(f"🔄 Procesando imagen {k+1}/{valor_total}: {fits_namer}")
        arch.barra_de_progreso(k,valor_total,"Analizando...","green")
        try:
            photom = Photometry_Data_Table(
                rutas, fits_namer, fits_pathr, catalogor,
                r=rr, r_in=r_inr, r_out=r_outr, center_box_size=center_box_size
            )

            if photom is not None:
                all_tables.append(photom)
            else:
                print(f"⚠️ Imagen {fits_namer} omitida (no se encontraron objetos válidos).")

        except Exception as e:
            print(f"❌ Error procesando {fits_namer}: {e}")

    print(f"✅ Se completó la fotometría de {len(all_tables)} imágenes exitosamente.")
    return all_tables


def creacion_periodograma(fechas_clean,flujos):
  '''
  Crea el peridograma de los datos ingresados con scipy
  
  '''
  # 🔹 Tus datos (Asegura que time tiene unidades)
  time = np.array(fechas_clean) * u.day  # Convierte a unidades de días
  flux = np.array(flujos)        

  # 🔹 Definir el rango de frecuencias
  min_period = 0.1 * u.day  
  max_period = 10 * u.day  
  frequency = np.linspace(1/max_period, 1/min_period, 10000)  

  # 🔹 Calcular el periodograma
  ls = LombScargle(time, flux)
  power = ls.power(frequency)

  # 🔹 Encontrar el período dominante
  best_frequency = frequency[np.argmax(power)]
  best_period = 1 / best_frequency
  print(f"mejor frecuencia:{best_frequency}")
  print(f"mejor periodo{best_period}")
  # 🔹 Graficar
  plt.figure(figsize=(8, 5))
  plt.plot(1/frequency, power, color="cyan", linewidth=2)
  plt.axvline(best_period.value, color="red", linestyle="--", label=f"Periodo: {best_period:.5f} días")
  plt.xlabel("Período (días)", fontsize=12)
  plt.ylabel("Potencia", fontsize=12)
  plt.xscale("log")
  plt.legend(f" Periodo más significativo: {best_period:.5f}")
  plt.title("Periodograma Lomb-Scargle", fontsize=14)
  plt.grid(True, linestyle="--", alpha=0.6)
  plt.savefig("Periodograma algol")
  
def light_curves_star(rutas, estrella, id_estrella):
    nombre_carpeta = "csv_out/"
  
    # Change to the csv_out directory if not already there.
    directorio = os.getcwd()
    if os.path.basename(directorio) != "csv_out":
        os.chdir(rutas['csv_out'])

    global tiempo
    global magnitud
    fechas = []
    magnitudes = []
  
    # Iterate over all CSV files in the current directory.
    for archivo in os.listdir("."):
        if archivo.endswith(".csv"):
            with open(archivo, mode='r', newline='', encoding='utf-8') as archivo_csv:
                lector = csv.reader(archivo_csv)
                # Iterate over rows in the CSV.
                for fila in lector:
                    # Compare the first field (ID) after stripping and lowering both sides.
                    if fila[0] == '3262756401298707584':
                        fechas.append(fila[5].strip())
                        try:
                            magnitudes.append(float(fila[3]))
                        except ValueError:
                            print(f"Error converting magnitude: {fila[3]}")
    
    tiempo = fechas
    print(f"Datos agregados correctamente, actualmente se cuenta con {len(magnitudes)} datos")
    
    # Return to the parent directory.
    os.chdir("..")
    
    # Convert the date strings to Julian dates.
    fechas_clean = [Time(f, format='isot', scale='utc').jd for f in tiempo]
    
    # Calculate flux values.
    flujos = [10**(-m/2.5) for m in magnitudes]
    datos = pd.DataFrame({
        'Fecha': fechas_clean,
        'Flujos': flujos
    })
    
    # Filter rows with flux greater than 0.04.
    #filtered_datos = datos[(datos['Fecha'] > 10) & (datos['Fecha'] < 18)]
    filtered_datos = datos
    plt.rcParams.update({
        'axes.facecolor': '#121212',
        'figure.facecolor': '#121212',
        'font.size': 10,
        'axes.labelcolor': 'white',
        'xtick.color': 'white',
        'ytick.color': 'white',
        'axes.edgecolor': 'white',
        'grid.color': '#404040',
        'grid.linestyle': '--',
        'grid.alpha': 0.3,
        'lines.color': 'cyan',
        'lines.linewidth': 2,
        'axes.titlecolor': 'white',
    })
    # Initialize a bundle
    #times = np.array(datos['Fecha'])
    #fluxes = np.array(datos['Flujos'])
    #b = phoebe.default_binary()
    #b.add_dataset('lc', times=times, fluxes=fluxes, dataset='lc01')
    #kernel = terms.SHOTerm(log_S0=0, log_omega0=0, log_Q=0)
    #b.add_gaussian_process(dataset='lc01', kernel=kernel)
    #b.run_compute()
    
   # afig, mplfig = b.plot(show=True)
    #mplfig.savefig("phoebe_gp_light_curve.png")
    alto, ancho = 4, 8
    plt.figure(figsize=(ancho, alto))  
    plt.scatter(filtered_datos['Fecha'], filtered_datos['Flujos'], linewidth=1)
    plt.xlabel("Tiempo Juliano", fontsize=10, labelpad=20)
    plt.ylabel("Flujo", fontsize=10, labelpad=20) 
    plt.title(("----------------Curva de luz para " + estrella + "----------------").upper(), fontsize=10, pad=10)
    plt.grid()
    plt.savefig("figura2.png")
    creacion_periodograma(fechas_clean,flujos)
def astrometric_routine(rutas,estrella,id_estrella):

  array_de_tablas = creacionTablasFotometricas(rutas,estrella)
  focus_object,filtro_final = adicionFiltros(array_de_tablas)
  filtro_resultado = interseccionFiltros(focus_object,filtro_final)     
  creacionTablasCsv(filtro_resultado,rutas,estrella)
  files.mover_objetos(".fits.out",rutas['fits_out'],rutas)
  
  curvas_de_luz_estrella(rutas,estrella,id_estrella)#Si esta la estrella deseada  en los datos se crea un nuevo .csv con los datos de algol 
def is_gaia_database_fallen():
    server_status = "Server is up"
    try:
    # Execute a simple query
      job = Gaia.launch_job_async("SELECT * FROM gaiadr2.gaia_source LIMIT 1")
      results = job.get_results()
      valor = False
    except Exception as e:
      error_message = str(e)
      if "500" in error_message:
        server_status = "The server is fallen"
        valor = True
      else:
        server_status = f"Error occurred: {error_message}"
    print(server_status)
    return valor

   
if __name__ == "__main__":
   
    rutina_astrometica()

