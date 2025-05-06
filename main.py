from all_scripts import astrometry as astrom
from all_scripts import files
from all_scripts import all_paths as paths

# Main block: uses paths built from the global variable 'route'
if __name__ == "__main__":
    print("Recommended stars: v1241 tau, algol, mu eridani")
    info_json = "info.json"
    star = input("Please enter the star: ")
    star_value = star

    star_id = astrom.gaia_ids(star)
    while star_id != True:
        little_star = input("Please enter a correct star name, use lowercase and only one space if the star has more than one word: ")      
        star_value = star
        star_id = astrom.gaia_ids(star)
    
    real_star_value = astrom.Star(star_value, 1000)

    files.ensure_star_json(info_json, star_value)
    paths = paths.define_paths_by_star(star_value)
    star_id = "3225773709223070464"
    print(f"Welcome to the program to find light curves for {star_value}")
    print()
    print("Next, you must choose one of the following options:")
    print("1. If this is the first time running the program, type: 1")
    print()
    print("2. To perform download and then analysis, type: 2")
    print()
    print("3. To perform only photometry on already downloaded images, type: 3")
    print()
    print("4. To plot already analyzed data, type: 4")
    option = input("Option to choose: ")
    option = int(option)

    if option == 1:
        # Install libraries via .sh script with pip install lib
        # files.run_sh_script(paths.bash_scripts + "install_libraries.sh")
        selected_sector = files.define_sector(paths, star_value)
        files.organize_commands_by_date(paths, star_value, selected_sector)
        astrom.save_to_csv(paths, star_value)
        files.run_curl_from_file(paths, star_value)
        # Once the Bash script stops due to threshold, proceed to photometry
        astrom.astrometric_routine(paths, star_value, star_id)
    elif option == 2:
        files.run_curl_from_file(paths, star_value)
        astrom.astrometric_routine(paths, star_value, star_id)
    elif option == 3:
        astrom.astrometric_routine(paths, star_value, star_id)
    elif option == 4:
        # astrom.light_curves_star()
        astrom.light_curves_star(paths, star_value, star_id)
    else:
        print("Please type only the number, without spaces or other values")
