from all_scripts import astrometria as astrom
from all_scripts import archivos as arch
from all_scripts import todas_las_rutas as ru
# Bloque principal: se usan las rutas construidas a partir de la variable global 'route'
if __name__ == "__main__":
                print("Estrellas recomendadas: v1241 tau,algol,mu eridani")
                info_json = "info.json"
                estrella =input("porfavor ingresa la estrella: ")
                estrella_valor = estrella
              
                id_estrella = astrom.gaia_ids(estrella)
                while id_estrella != True:
                         estrellita =input("porfavor ingresa una estrella correcta, ingresala en minusculas y usa solo un espacio si la estrella contiene mas de una palabra: ")      
                         estrella_valor = estrella
                         id_estrella = astrom.gaia_ids(estrella)
                valor_estrella_real = astrom.Star(estrella_valor,1000)

                arch.ensure_star_json(info_json,estrella_valor)
                rutas= ru.definicion_rutas_por_estrella(estrella_valor)
                id_estrella = "3225773709223070464"
                print(f"Bienvenido al programa para encontrar las curvas de luz de {estrella_valor}")
                print(" ")
                print("a continuación debes seleccionar una de las dos opciones")
                print("1.Si es la primera vez que ejecutas el programa escribe: 1")
                print(" ")
                print("2.Para realizar el proceso de la descarga y luego análisis escribe: 2")
                print(" ")
                print("3.Para realizar solo la fotometría de imagenes descargadas escribe: 3")
                print(" ")
                print("4.Para graficar datos ya analizados escribe: 4")
                opcion = input("opción a escoger: ")
                opcion = int(opcion)
                if opcion == 1:
                #Instalación de librerias desde la ejecución del .sh con el comando pip install lib
                
                    #arch.ejecutar_sh(ru.bash_scripts+"instalacion_librerias.sh")
                    sector_seleccionado = arch.definir_sector(rutas,estrella_valor)
                    arch.organizar_comandos_por_fecha(rutas,estrella_valor,sector_seleccionado)
                    astrom.save_to_csv(rutas,estrella_valor)
                    arch.ejecutar_curl_desde_archivo(rutas,estrella_valor)
                    # Una vez que el script de Bash se detenga por alcanzar el umbral, se procede a fotometría
                    astrom.rutina_astrometica(rutas,estrella_valor,id_estrella)
                elif opcion == 2:
                    arch.ejecutar_curl_desde_archivo(rutas,estrella_valor)
                    astrom.rutina_astrometica(rutas,estrella_valor,id_estrella)
                elif opcion == 3:
                    astrom.rutina_astrometica(rutas,estrella_valor,id_estrella)
                elif opcion == 4:
                    #astrom.curvas_de_luz_estrella()
                    astrom.curvas_de_luz_estrella(rutas,estrella_valor,id_estrella)
                else:
                      print("Porfavor escribe solo el numero sin espacios ni otros numeros o valores")
                    
                        


