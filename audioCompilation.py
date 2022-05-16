# Read files and combine audio information.
# The file uses the files *csv provided from the optimization algorithm and uses it to compile audio file.

# Author : Hemal Naik

import os
import glob
import pandas as pd
import librosa
import soundfile


def getDirFromFile(hour,min):
    """
    The function creates a text for going through the folders. The text is compatible for files created with the program.
    :param hour: int
    :param min: int
    :return: str
    """
    if min < 15:
        min_mark = "00"
    elif min < 30 and min >= 15:
        min_mark = "15"
    elif min < 45 and min >= 30:
        min_mark = "30"
    else:
        min_mark = "45"

    hour_mark = str(hour)

    return hour_mark + "-" + min_mark

def prepDateText(date):
    """
    Prepare text for the data based on the given data, the string is in required format.
    :param date: int
    :return: str
    """

    day = date.split("-")[2]
    if int(day) < 10 :
        day_text = "0" + day
    else:
        day_text = str(day)

    year = date.split("-")[0]

    month = date.split("-")[1]

    return year + "-" + month + "-" + day_text

def prepTimeText(hour, min, sec):
    """
    Prepare text to combine time for reading audio files
    :param hour: int
    :param min: int
    :param sec: int
    :return: str
    """

    if sec < 10:
        sec_text = "0" + str(sec)
    else:
        sec_text = str(sec)

    if min < 10:
        min_text = "0" + str(min)
    else:
        min_text = str(min)

    hour_text = str(hour)

    return hour_text + "-" + min_text + "-" + sec_text

# Main function runs the file with given locations. Please update the file locations based on your local file path.
if __name__ == '__main__':
    # Path for the audio files
    audio_file_path = "X:\\Nora_Data\\For Barn Methods\\Starling_Audio"

    csv_file_path = "X:\\HemalData\\Software Dev\\audioData"

    # Define directories to go through
    folderNames =  ["7th","8th","9th","10th"]
    # hours = ["11","12","13"]
    # mins = ["00","15","30","45"]

    # Prefix and suffix for the audio files for reading from folder.
    audio_file_prefix = "trial1_Chan"
    audio_file_suffix = "_ADC05000mV_00dB.wav"

    audio_compilation_file = "compilation.wav"
    samplingRate = 0
    # Read the *.csv files from each folder

    for folder in folderNames:
        compiled_sound_data = []
        csv_data_path_day = os.path.join(csv_file_path, folder)
        audio_data_path_day = os.path.join(audio_file_path, folder)

        # Fetch .csv files from the provided folder
        csv_file = glob.glob(os.path.join(csv_data_path_day,"*.csv"))
        print(f"File : ", csv_file[0])
        # Prepare final name of compilation file
        audio_compilation_file_path = os.path.join(csv_data_path_day, folder + audio_compilation_file)

        # Go through each file in the csv and get
        data_Frame = pd.read_csv(csv_file[0])
        total_points = data_Frame.shape[0]
        for index in range(0,total_points):

            date_text = prepDateText(data_Frame["Y-M-D"].iloc[index])

            # Find data from the file which allows identification of the audio file based on the entry of data frame
            hour = data_Frame["HH"].iloc[index]
            min = data_Frame["MM"].iloc[index]
            sec = data_Frame["SS"].iloc[index]
            dir_time = getDirFromFile(hour,min)
            audio_data_path_day_time = os.path.join(audio_data_path_day,dir_time)

            loudest_Channel = data_Frame["LoudestChannel"].iloc[index]
            if loudest_Channel < 10:
                channel_text = "0" + str(loudest_Channel)
            else:
                channel_text =  str(loudest_Channel)

            time_text = prepTimeText(hour, min, sec)

            # Prepare names of the audio files
            audioFile = audio_file_prefix + channel_text + "_" + date_text + "_" + time_text + audio_file_suffix
            sample_audio_file  =  audio_file_prefix + channel_text + "_" + date_text + "_" + time_text + "_sample" + audio_file_suffix

            # Prepare sampling time, i.e. determine clipping duration of the audio clip.
            sample_base_seconds = data_Frame["SS"].iloc[index]
            sample_event_seconds = data_Frame["event-SS"].iloc[index]
            sample_time = sample_event_seconds - sample_base_seconds
            sample_number = round( sample_time * 100000)

            sampling_width = 150000
            sample_start = sample_number - 50000
            sample_end = sample_number + sampling_width
            if sample_start < 0:
                sample_start = 0
                sample_end = sample_start + sampling_width

            if sample_end > 500000:
                sample_end = 500000
                sample_start = 500000 - sampling_width

            focal_audio_file_path = os.path.join(audio_data_path_day_time, audioFile)
            sample_audio_file_path = os.path.join(csv_data_path_day, sample_audio_file)

            if os.path.exists(focal_audio_file_path):
                print(f"File Name: {audioFile} exists")

            # Load the audio files, then take required clipping from file
            x, samplingRate = librosa.load(focal_audio_file_path, sr=None)
            samplesOfChoice = x[sample_start:sample_end]
            soundfile.write(sample_audio_file_path, samplesOfChoice, samplingRate)

            # Add samples to a file, the clipping from each file gets added one after another.
            compiled_sound_data = compiled_sound_data + list(samplesOfChoice)

        # Write the final sound file
        soundfile.write(audio_compilation_file_path, compiled_sound_data, samplingRate)


