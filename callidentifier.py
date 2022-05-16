'''
Part 1: This file is created to skim through all X(5/10) second sound clips from all the channels and then pick our the one which has maximum sound intensity.
The output is a file that suggests maximum intensity recorded within the given *.wav file and the timing of the sample.
THe assumption is that loudest noise is the relevant noise, of course there could be more calls in the five seconds but for now we consider a simple model.
'''
# Author : Hemal Naik

import os
from matplotlib import pyplot as plt
import IPython.display as ipd
import librosa
import glob
import csv


def print_plot_play(x, Fs, text=''):
    """
    Prints information about an audio singal, 2. plots the waveform, and 3. Creates player
    :param x: Input signal
    :param Fs: Sampling rate of x
    :param text: Text to print
    :return:
    """

    plt.figure(figsize=(8, 2))
    plt.plot(x, color='gray')
    plt.xlim([0, x.shape[0]])
    plt.ylim([-0.2, 0.2])
    plt.xlabel('Time (samples)')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.savefig(text+".jpg")
   # plt.show()
    ipd.display(ipd.Audio(data=x, rate=Fs))

def read_audio(name):
    """
    Reads the audio files provided and returns no of samples with max sample (amplitude)
    :param name: str
    :return: int, list
    """
    fn_wav = str(name)
    x, Fs = librosa.load(fn_wav, sr=None)
    #print_plot_play(x=x, Fs=Fs, text=f'{name}')
    maxAmp = max(x)
    x = list(x)
    sampleNo = x.index(maxAmp)
    return max(x), sampleNo

def read_files(path):
    """
    Reads the given path of directory, finds all .wav files and returns list of all files in the dir
    :param path: str
    :return: list
    """
    # return all the wav files in the path as list
    filenames= glob.glob(os.path.join(path, "*.wav"))
    return filenames

def plot_intensities(ampDict):
    """
    Plots intensities of the provided samples
    :param ampDict: dict
    :return: None
    """
    lists = ampDict.items()
    x,y = zip(*lists)
    x = range(len(x))
    plt.figure(figsize=(8, 2))
    #plt.plot(x, color='gray')
    plt.plot(x, y)
    plt.xlim([0, len(x) ]) #x.shape[0]])
    plt.ylim([-0.2, 0.2])
    plt.xlabel('Samples')
    plt.ylabel('Amplitude')
    plt.tight_layout()

    #plt.show()
    plt.savefig("plotIntensities.jpg")

def findInfoFromName(audioFileName, lengthOfAudio):
    """
    Read the provided file name and get information about recording date and time from file name. The data is
    prepared as a dictionary.
    :param audioFileName: str
    :param lengthOfAudio: int
    :return: dict
    """
    dict = {}
    audioFileName = os.path.basename(audioFileName)
    sections = audioFileName.split("_")
    # Selection done from behind because some files have _ in their names and this makes things confusing but
    # naming protocol seems robust if we see if backwards
    channelSection = sections[-5].split("Chan")
    dateSection = sections[-4].split("-")
    timeSection = sections[-3].split("-")

    dict["Channel"] = channelSection[1]
    dict["Year"] = dateSection[0]
    dict["Month"] = dateSection[1]
    dict["Day"] = dateSection[2]
    dict["Hour"] = timeSection[0]
    dict["Minute"] = timeSection[1]
    dict["Seconds"+"_"+str(lengthOfAudio)] = timeSection[2]

    return dict

def create_empty_dict(list):
    """
    Create an empry dict for the provided list
    :param list: list
    :return: dict
    """
    dict = {}
    for i in list:
        dict[i] = 0

    return dict

if __name__ == '__main__':
    # Provide directory of the files and folder name or subfolder names for processing the data
    # Part 1 : Prepare list of folders to scan for the audio files, depending on the data collection the organization of
    # data may differ. Ideally list = [ Path\\ Dir \\ *.wav, Path\\ Dir \\ *.wav, Path\\ Dir \\ *.wav]
    starlingData = False
    pathList = []
    if starlingData:
        path = "X:\\Nora_Data\\For Barn Methods\\Starling_Audio"

        # Define directories to go through
        #folderNames = ["7th","8th","9th","10th"]

        folderNames = ["8th","9th"]
        hours = ["11","12","13"]
        mins = ["00","15","30","45"]

        # Create a list of directories from the defined directory names
        pathList = []
        for dir in folderNames:

            # Add the subfolder with specific date to the path
            path_with_date = os.path.join(path,dir)

            for hour in hours:
                for min in mins:
                    time = hour + "-" + min
                    # Create path for subdirectory having the sound files : path\\date\\hour-min
                    path_with_date_hour_min = os.path.join(path_with_date,time)

                    # Prepare a list of all the directories within the given folder structure
                    if os.path.exists(path_with_date_hour_min):
                        pathList.append(path_with_date_hour_min)
                        print(path_with_date_hour_min)

    else:
        # Main directory having all audio files
        path = "X:\\Mate_Data\\MALTA_Recordings\\2021_05_11"
        #folderNames = ["batlure", "barnoutline", "batluremoving", "birdcalls", "mobile", "mobile2", "static"]
        folderNames = ["batluremoving", "birdcalls", "mobile", "mobile2", "static"]
        pathList = []
        for dir in folderNames:
            path_with_dir = os.path.join(path,dir)
            if os.path.exists(path_with_dir):
                pathList.append(path_with_dir)
                print(path_with_dir)

    # Part 2 : Go through list of all the directories and process audio files in those directories
    # The output is a .csv file for each directory. The .csv file each row contains information about
    # loudest sound for a particular duration for each channel. Each clip can be X seconds based on the setting in the
    # audio recording file. We also enter the intensity and sample timing of the sound in that particular file

    for path in pathList:
        # get list of all the audio files (*.wav) from the given path
        filenames = read_files(path)
        lengthOfAudio = 0

        # Define the duration of each audio file
        if starlingData:
            lengthOfAudio = 5 # in seconds
        else:
            lengthOfAudio = 10

        # Define filename for the final .csv file
        csvFile = "dataBase.csv"
        csvFilePath = os.path.join(path,csvFile)
        print(f'Path:{csvFilePath}')

        # Create handler for csv storage file and write header.
        csvFileHandler = open(csvFilePath, "w", newline="")
        csvWriter = csv.writer(csvFileHandler, delimiter = ",")
        header = ["Filename", "Channel", "Year", "Month", "Day", "Hour", "Minute","Seconds" + "_" + str(lengthOfAudio), "Max_intensity", "Max_sample_timing"]
        csvWriter.writerow(header)

        # Create empty dict
        dataDict = create_empty_dict(header)

        # Go through each file and extract call amplitudes etc.
        for name in filenames:
            dateTimeInfo_dict = findInfoFromName(name, lengthOfAudio)
            dataDict.update(dateTimeInfo_dict)
            dataDict["Filename"] = os.path.basename(name)
            dataDict["Max_intensity"], dataDict["Max_sample_timing"] = read_audio(name)
            print(f'File:{name}')
            # Get all values as list
            values = list(dataDict.values())
            csvWriter.writerow(values)

        #close the file
        csvFileHandler.close()
