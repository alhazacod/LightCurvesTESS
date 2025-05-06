from all_scripts import files
route = "./"
imagenes_cortadas = route+"imagenes_cortadas/"
archivo_catalogo = route+"datos_astrometria_modificados/" 
bash_scripts = route+"bash_scripts/"
csv_out = route+"csv_out/"
fits_out = route+"fits_out/"
imagenes = route+"imagenes/"
def define_paths_by_star(estrella):
    ruta_estrella = f"{estrella}/"
    rutas_array = {'route':route + ruta_estrella,'imagenes_cortadas':ruta_estrella+"imagenes_cortadas/",'archivo_catalogo':ruta_estrella+"datos_astrometria_modificados/" ,
    'bash_scripts': route+ruta_estrella+"bash_scripts/",
    'csv_out': route+ruta_estrella+"csv_out/",
    'fits_out': route+ruta_estrella+"fits_out/",
    'imagenes': route+ruta_estrella+"imagenes/"}
    for key in rutas_array:
        if key == 'archivo_catalogo':
            files.creacion_directorio(ruta_estrella+"datos_astrometria_modificados/")
        else:
            files.creacion_directorio(rutas_array[key])
    return rutas_array
