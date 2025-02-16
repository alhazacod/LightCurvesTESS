from all_scripts import astrometria as astrom
from all_scripts import archivos as arch
from all_scripts import todas_las_rutas as ru

# Variable global para la ruta principal de la organización de carpetas


# Bloque principal: se usan las rutas construidas a partir de la variable global 'route'
if __name__ == "__main__":
                #Instalación de librerias desde la ejecución del .sh con el comando pip install lib
                arch.ejecutar_sh(ru.bash_scripts+"instalacion_librerias.sh")
                coords = astrom.get_coordinates_from_name("algol")

                #print("Las coordenadas de algol son:", coords)

                #astrom.save_to_csv()
                arch.ejecutar_curl_desde_archivo()

                # Una vez que el script de Bash se detenga por alcanzar el umbral, se procede a fotometría
                #astom curvas_de_luz_estrella()
                astrom.rutina_astrometrica()
# Observatorio Astronómico Nacional 2025 

