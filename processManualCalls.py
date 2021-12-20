import math
import csv
import pandas as pd
import os
#Process

# Find time from the acoustic file
def find_sampleno_from_call_time(fifteentime):
    # Compute the time of call in terms of seconds
    mins = math.floor(fifteentime / 60)
    secs_within_minute = fifteentime - mins*60
    baseSecondas = math.floor(secs_within_minute / 5) * 5
    time_of_call = secs_within_minute - baseSecondas
    sample = math.floor(time_of_call * 100000)

    return time_of_call, sample
    #

# Find the right folder for the audio files

def process_data(dataFrame, audio_file_path):
    print("hey")
    fifteenTime = dataFrame["fifteentime"].tolist()
    time_section = dataFrame["timesection"].tolist()
    file_names = dataFrame["soundfilename"].tolist()

    for iterator in range(0,len(fifteenTime)):
        hrs = str(time_section[iterator]).split("_")[0]
        mins = str(time_section[iterator]).split("_")[1]
        folder_name = os.path.join(audio_file_path, hrs+"-"+mins)
        file_name = os.path.join(folder_name, str(file_names[iterator]))
        if os.path.exists(file_name):
            print(f'Processing audio file: {folder_name}')
            callTime, sample_no = find_sampleno_from_call_time(fifteenTime[iterator])

        queryText = 


if __name__ == '__main__':
    """
    """
    name = "D:\\Barn Stuff\\VerificationFile\\trial1_Chan14_2019-12-09_11-15-00to13-00_OnlyVerrifiedCalls_modified.csv"
    dataFrame = pd.read_csv(name)
    audio_file_path = "D:\\Barn Stuff\\AudioSamples"
    process_data(dataFrame, audio_file_path)