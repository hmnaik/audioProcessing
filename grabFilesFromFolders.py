## This file is purely created to copy files from one place to another
# Author : Hemal Naik

import os
import shutil


if __name__ == '__main__':
    """
    """
    path = "X:\\Nora_Data\\For Barn Methods\\Starling_Audio"
    output_path = "X:\\HemalData\\Software Dev\\audioProcessing"
    # Define directories to go through
    folderNames = ["7th","8th","9th","10th"]
    hours = ["11", "12", "13"]
    mins = ["00", "15", "30", "45"]

    newDirectory = "fourDayData"
    output_dir = os.path.join(output_path,newDirectory)
    files = ["correlation.csv","dataBase.csv","updated_dataBase.csv"]
    try:
        os.mkdir(output_dir)
    except OSError as error:
        print(error)

    # Create a list of directories from the defined directory names
    pathList = []
    for dir in folderNames:
        path_with_date = os.path.join(path, dir)
        for hour in hours:
            for min in mins:
                time = hour + "-" + min
                path_with_date_hour_min = os.path.join(path_with_date, time)
                # Add only those directories that exist
                if os.path.exists(path_with_date_hour_min):
                    destination_with_day = os.path.join(output_dir,dir)
                    if not os.path.exists(destination_with_day):
                        os.mkdir(destination_with_day)
                    destination_with_day_time = os.path.join(destination_with_day, time)
                    os.mkdir(destination_with_day_time)
                    for file in files:
                        shutil.copy(os.path.join(path_with_date_hour_min,file),destination_with_day_time)
                        print(f"Copying {os.path.join(path_with_date_hour_min,file)} --> {destination_with_day_time}")
