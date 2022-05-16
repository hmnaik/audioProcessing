'''
Part 1: This file is created to skim through all 5 second sound clips from all the channels and then pick our the one which has maximum sound intensity.
The output is a file that suggests maximum intensity recorded within the given *.wav file and the timing of the sample.
THe assumption is that loudest noise is the relevant noise, of course there could be more calls in the five seconds but for now we consider a simple model.
'''
# Author : Hemal Naik

import os
import numpy as np
from matplotlib import pyplot as plt
import IPython.display as ipd
import librosa
import glob
import csv
import pandas as pd

# matplotlib inline
def print_plot_play(x, Fs, text=''):
    """1. Prints information about an audio singal, 2. plots the waveform, and 3. Creates player

    Notebook: C1/B_PythonAudio.ipynb

    Args:
        x: Input signal
        Fs: Sampling rate of x
        text: Text to print
    """
    #print('%s Fs = %d, x.shape = %s, x.dtype = %s' % (text, Fs, x.shape, x.dtype))
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
    # Use a breakpoint in the code line below to debug your script.
    #fn_wav = os.path.join('..', 'data', 'B', 'D:\\Barn Stuff\\trial1_Chan07_2019-12-09_11-15-00_ADC05000mV_00dB.wav')
    fn_wav = str(name)
    x, Fs = librosa.load(fn_wav, sr=None)
    #print_plot_play(x=x, Fs=Fs, text=f'{name}')
    maxAmp = max(x)
    x = list(x)
    sampleNo = x.index(maxAmp)
    return max(x), sampleNo

def read_files(path):
    # return all the wav files in the path as list
    filenames= glob.glob(os.path.join(path, "*.wav"))
    return filenames

def plot_intensities(ampDict):
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
    dict = {}

    for i in list:
        dict[i] = 0

    return dict

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Path for the audio files
    #path = "D:\\Barn Stuff\\AudioSamples"
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
            path_with_date = os.path.join(path,dir)
            for hour in hours:
                for min in mins:
                    time = hour + "-" + min
                    path_with_date_hour_min = os.path.join(path_with_date,time)
                    # Add only those directories that exist
                    if os.path.exists(path_with_date_hour_min):
                        pathList.append(path_with_date_hour_min)
                        print(path_with_date_hour_min)
    else:
        path = "X:\\Mate_Data\\MALTA_Recordings\\2021_05_11"

        #folderNames = ["batlure", "barnoutline", "batluremoving", "birdcalls", "mobile", "mobile2", "static"]
        folderNames = ["batluremoving", "birdcalls", "mobile", "mobile2", "static"]
        pathList = []
        for dir in folderNames:
            path_with_dir = os.path.join(path,dir)
            if os.path.exists(path_with_dir):
                pathList.append(path_with_dir)
                print(path_with_dir)



    # Go through each path and process each folder
    for path in pathList:

        # get list of all the audio files (*.wav) from the given path
        filenames = read_files(path)
        lengthOfAudio = 0
        if starlingData:
            lengthOfAudio = 5 # in seconds
        else:
            lengthOfAudio = 10
        # filename for storing data
        csvFile = "dataBase.csv"
        csvFilePath = os.path.join(path,csvFile)
        print(f'Path:{csvFilePath}')

        # Create handler for csv storage file and write header
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
