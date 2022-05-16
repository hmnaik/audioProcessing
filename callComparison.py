'''
Part 2: This file would pick up the output of callIdentifies.py. This script picks up the channel that reports highest intensity of sound
within a 5 second recording. The sample timing of the loudest channel is idenfied as primary channel assumed to be closest to the source.
This scrip takes the timing of the sample of the loudest channel, then finds samples with highest intensity along the same time window in other channels.
This way we can narrow down the calls to one single sound and possibly try to triangulate the sound.
'''

import os
import pandas as pd
import librosa
#
def read_csv(file_name):
    """
    :param file_name:
    :return:
    """
    dataBase = pd.read_csv(file_name)
    return dataBase

#
def get_query_value(hour,min,seconds):
    # Convert all values to string
    hour_str = str(hour)
    if hour < 10:
        hour_str = "0" + hour_str
    min_str = str(min)
    if min < 10:
        min_str = "0" + min_str
    sec_str = str(seconds)
    if seconds < 10:
        sec_str = "0" + sec_str
    # Get query value
    query = hour_str + "-" + min_str + "-" + sec_str

    return query
#
def grab_data_for_given_query(dataBase,query_string):

    # This subset should have information about all the channels in the given time series

    subSet = dataBase[dataBase["Filename"].str.contains("_"+query_string+"_")]
    return subSet

#def update_values(subset_database):
def process_subset(data_subset):
    # find max intensity

    max_intensity_id = data_subset["Max_intensity"].idxmax()
    sample_number = data_subset["Max_sample_timing"].loc[max_intensity_id]
    file_name = data_subset["Filename"].loc[max_intensity_id]

    return file_name, sample_number


def findMaxValues(path_to_files,file_names,sample_min, sample_max):

    sample_locations = []
    amp_values = []
    for file in file_names:
        # Go thought all the files
        audio_file_path = os.path.join(path_to_files,file)
        fn_wav = str(audio_file_path)

        x, Fs = librosa.load(fn_wav, sr=None)
        if sample_max > len(x):
            sample_max = len(x)
        if sample_min < 0:
            sample_min = 0

        # Fine sample values
        selected_sample_values = x[sample_min:sample_max]
        #print(f'Sample size : {len(selected_sample_values)}')
        maxAmp = max(selected_sample_values)

        # The implementation below is to avoid a bug, that if any similar value exist outside the range then we would not really get the right index
        selected_sample_values = list(selected_sample_values)
        sampleNo = selected_sample_values.index(maxAmp)
        sampleNo = sampleNo + sample_min

        # Create a list of the new values
        sample_locations.append(sampleNo)
        amp_values.append(maxAmp)

    return sample_locations, amp_values

def process_given_folder_batch(path_to_files, startHour= 0, endHour = 0, startMin = 0, endMin = 0 , secondStart = 0, secondInterval=0):

    path_database = os.path.join(path_to_files, "database.csv")
    if os.path.exists(path_database) == False:
        return False

    seconds = [i for i in range(secondStart, 60, secondInterval)]
    min_sample_range = 1000*3
    max_sample_range = 3000*3

    dataBase = read_csv(path_database)
    updatedDataBase = []
    min = startMin
    hour = startHour
    while hour < (endHour+1):
        while min < (endMin+1):
            for sec in seconds:
                query_str = get_query_value(hour, min, sec)
                data_subset = grab_data_for_given_query(dataBase.copy(), query_str)
                print(f'Query: {query_str} : Data Size : {data_subset.shape} ')
                if data_subset.empty:
                    print(f'Query: {query_str} \n ')
                    print("No data found for the query")
                    continue
                max_file_name, sample_number = process_subset(data_subset.copy())
                # All file names
                file_names = data_subset["Filename"]

                sample_locations, amp_values = findMaxValues(path_to_files, file_names, sample_number - min_sample_range,
                                                             sample_number + max_sample_range)

                data_subset["Max_intensity"] = amp_values
                data_subset["Max_sample_timing"] = sample_locations

                updatedDataBase.append(data_subset)

            min = min + 1

        min = 0
        hour = hour+1

    final_dataset = pd.concat(updatedDataBase)
    newFileName = os.path.join(path_to_files, "updated_dataBase.csv")
    final_dataset.to_csv(newFileName, index=False)
    return True

def process_given_folder (path_to_files, startHour, startMin, secondStart = 0, secondInterval = 5):

    startMin_str = str(startMin)
    if startMin < 10:
        startMin_str = "0" + startMin_str
    path_to_files = os.path.join(path_to_files, str(startHour) + "-" + str(startMin_str))
    path_database = os.path.join(path_to_files, "database.csv")
    if os.path.exists(path_database) == False:
        return False

    timeInterval = 15
    endMin = startMin + timeInterval
    seconds = [i for i in range(secondStart, 60, secondInterval)]
    min_sample_range = 1000
    max_sample_range = 3000

    dataBase = read_csv(path_database)
    updatedDataBase = []
    min = startMin
    while min < endMin:
        for sec in seconds:
            query_str = get_query_value(startHour, min, sec)
            data_subset = grab_data_for_given_query(dataBase.copy(), query_str)
            print(f'Query: {query_str} : Data Size : {data_subset.shape} ')
            if data_subset.empty:
                print("No data found for the query")
                break
            max_file_name, sample_number = process_subset(data_subset.copy())
            # All file names
            file_names = data_subset["Filename"]

            sample_locations, amp_values = findMaxValues(path_to_files, file_names, sample_number - min_sample_range,
                                                         sample_number + max_sample_range)

            data_subset["Max_intensity"] = amp_values
            data_subset["Max_sample_timing"] = sample_locations

            updatedDataBase.append(data_subset)

        min = min + 1

    final_dataset = pd.concat(updatedDataBase)
    newFileName = os.path.join(path_to_files, "updated_dataBase.csv")
    final_dataset.to_csv(newFileName, index=False)

    return True


if __name__ == "__main__":
    """
    """
    starlingData = False
    if starlingData :
        path = "X:\\Nora_Data\\For Barn Methods\\Starling_Audio"

        # Define directories to go through
        dir_with_dates = ["7th", "8th", "9th", "10th"]
        dir_with_dates = ["8th","9th"]
        for dir in dir_with_dates:

            startSec = 0

            path_to_files = os.path.join(path,dir)
            if os.path.exists(path_to_files):
                print(f' Processing file: {path_to_files}')
                startHours = [11,12, 13]
                startMins = [0,15,30,45]
                # The structure of processing files is slightly different because minutes and hours are crucial to find right files to process and compare.
                for startHour in startHours:
                    for startMin in startMins:
                        # Special case with the dataset
                        if dir == "7th" and startHour== 11 : # Covers 7th//11-15,11-30,11-45
                            startSec = 2
                        elif dir == "7th" and startHour== 12 and startMin == 0: # 7th//12-00
                            startSec = 2
                        elif dir == "7th" and startHour== 12 and startMin != 0: # 7th//
                            startSec = 1
                        elif dir == "7th" and startHour== 13: # 7th//
                            startSec = 1
                        elif dir == "8th":
                            startSec = 3
                        else:
                            startSec = 0

                        final_dataset = process_given_folder(path_to_files, startHour, startMin, startSec)

                        if final_dataset == False:
                            print(f'Query : {startHour}-{startMin}  can not be found')
            else:
                print(f'Path does not exist : {path_to_files}')
    else:

        path = "X:\\Mate_Data\\MALTA_Recordings\\2021_05_11"
        folderNames = ["batlure", "barnoutline", "batluremoving", "birdcalls", "mobile", "mobile2", "static"]
        #Format : [startHour, endHour, startMin, endMin , secondStart, secondInterval]
        #dict = {"batlure":[18,18,32,32,23,10], "barnoutline":[17,17,27,28,8,10],"batluremoving":[18,18,33,34,15,10],"birdcalls":[17,18,0,59,31,10],
        #        "mobile":[15,15,33,37,10],"mobile2":[15,15,55,57,10],"static":[12,32,32,23,10]}

        #dict = {"batlure": [3, 10], "barnoutline": [8, 10],"batluremoving": [5, 10],"birdcalls": [1, 10]
        folderNames = [ "mobile", "mobile2", "static"]
        dict = {"mobile":[4,10],"mobile2":[2,10],"static":[9,10]}

        for dir in folderNames:
            path_with_dir = os.path.join(path, dir)
            if os.path.exists(path_with_dir):
                startHour, endHour, startMin, endMin  = [0, 23, 0, 59]
                [secondStart, secondInterval] = dict[dir]
                print(path_with_dir)
                final_dataset = process_given_folder_batch(path_with_dir, startHour = startHour, endHour= endHour, startMin= startMin, endMin= endMin, secondStart= secondStart, secondInterval= secondInterval)
                if final_dataset == False:
                    print(f"Path : {path_with_dir} did not process")
            else:
                print(f"Path : {path_with_dir} does not exist")