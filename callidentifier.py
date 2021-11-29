# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

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

def findInfoFromName(audioFileName):
    dict = {}
    audioFileName = os.path.basename(audioFileName)
    sections = audioFileName.split("_")
    channelSection = sections[1].split("Chan")
    dateSection = sections[2].split("-")
    timeSection = sections[3].split("-")

    dict["Channel"] = channelSection[1]
    dict["Year"] = dateSection[0]
    dict["Month"] = dateSection[1]
    dict["Day"] = dateSection[2]
    dict["Hour"] = timeSection[0]
    dict["Minute"] = timeSection[1]
    dict["Seconds_5"] = timeSection[2]

    return dict

def create_empty_dict(list):
    dict = {}

    for i in list:
        dict[i] = 0

    return dict

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Path for the audio files
    path = "D:\\Barn Stuff\\AudioSamples"
    # get list of all the audio files (*.wav) from the given path
    filenames = read_files(path)

    # filename for storing data
    csvFile = "dataBase.csv"
    csvFilePath = os.path.join(path,csvFile)
    print(f'Path:{csvFilePath}')

    # Create handler for csv storage file and write header
    csvFileHandler = open(csvFilePath, "w", newline="")
    csvWriter = csv.writer(csvFileHandler, delimiter = ",")
    header = ["Filename", "Channel", "Year", "Month", "Day", "Hour", "Minute","Seconds_5", "Max_intensity", "Max_sample_timing"]
    csvWriter.writerow(header)

    # Create empty dict
    dataDict = create_empty_dict(header)
    # Go through each file and extract call amplitudes etc.
    for name in filenames:
        dateTimeInfo_dict = findInfoFromName(name)
        dataDict.update(dateTimeInfo_dict)
        dataDict["Filename"] = os.path.basename(name)
        dataDict["Max_intensity"], dataDict["Max_sample_timing"] = read_audio(name)
        print(f'File:{name}')
        # Get all values as list
        values = list(dataDict.values())
        csvWriter.writerow(values)

    #close the file
    csvFileHandler.close()
