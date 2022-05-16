'''
Part 3: The file is created to computer cross correlation between the audio samples.
This program depends on the output of another file - callComparison.py
A typical *.csv input to this file contains information about loudest channel among the 23 channels, for each 5 second clip.
The sample timing of loudest channel is noted and samples along the same timeline are extracted from the other channels to compare similarity of the signal.
This allows us to identify how similar are the calls and ideally channels would report samples near or father from the current channel.
'''

# Author : Hemal Naik

import os
import pandas as pd
import librosa
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

def getSampleData(file, minRange, maxRange):
    """
    The function extracts sample values of the given sound file for the given time range
    :param file: str
    :param minRange: int
    :param maxRange: int
    :return: list
    """

    #todo: Workout plan to do padding of data

    samples, Fs = librosa.load(file, sr=None)
    if minRange < 0:
        minRange = 0
        samples = samples[minRange:maxRange]
        print(f"Min range breach size: {len(samples)}")
    elif maxRange > len(samples):
        maxRange = len(samples)
        samples = samples[minRange:maxRange]
        print(f"Max range breach size: {len(samples)}")
    else:
        samples = samples[minRange:maxRange]

    return samples

def find_correlation_points(soundFiles, sampleTiming, focalChannel, path_to_files, min_sample_range = 1000, max_sample_range = 3000):
    """
    The function compute correlation (similarity) between the given sound files. The function is given all necessary infromation to
    clip the required sampling range from audio file. The funtion finds similarity between the focal signal and
    other channel for same time range. The return is correlation value and the time lag.
    :param soundFiles: list
    :param sampleTiming: int
    :param focalChannel: int
    :param path_to_files: str
    :param min_sample_range: int
    :param max_sample_range: int
    :return: dict, dict
    """
    correlationDataDict = {}
    lagDataDict = {}

    # Find sample values for all the files
    focalFile = [i for i in soundFiles if str(focalChannel) in i ]

    focalFile_path = os.path.join(path_to_files, focalFile[0])
    dataOnFocalFile = getSampleData(focalFile_path, sampleTiming-min_sample_range, sampleTiming+max_sample_range)

    for file in soundFiles:
        # Select the file that is not focal file
        if file == focalFile:
            #print("File")
            correlation = 0
            correlationDataDict[file] = correlation
        else:
            queryFilePath = os.path.join(path_to_files, file)
            dataOnQueryFile = getSampleData(queryFilePath, sampleTiming-min_sample_range, sampleTiming+max_sample_range)

            #plot
            corr_values= signal.correlate( dataOnQueryFile, dataOnFocalFile , mode="full", method= "auto")
            maxCorr = np.max(corr_values)

            #plot
            #print(corr_values)

            lags = signal.correlation_lags(len(dataOnFocalFile),len(dataOnQueryFile), mode = "full")
            lag = lags [np.argmax(corr_values)]

            # The following code provides graph of the correlation function if needed
            #corr_values = numpy.correlate(dataOnFocalFile,dataOnQueryFile)
            #print(f"Corrleation: {corr_values}")
            # fig, (ax_orig, ax_noise, ax_corr) = plt.subplots(3, 1, sharex=True)
            # ax_orig.plot(dataOnFocalFile)
            #
            # #ax_orig.plot(clock, sig[clock], 'ro')
            #
            # ax_orig.set_title('Focal signal ')
            #
            # ax_noise.plot(dataOnQueryFile)
            #
            # ax_noise.set_title('Query signal')
            #
            # ax_corr.plot(corr_values)
            #
            # #ax_corr.plot(clock, corr[clock], 'ro')
            #
            # #ax_corr.axhline(0.5, ls=':')
            #
            # ax_corr.set_title('Cross-correlated signal')
            #
            # #ax_orig.margins(0, 0.1)
            #
            # fig.tight_layout()
            #
            # plt.show()

            correlationDataDict[file] = maxCorr
            lagDataDict[file] = lag

    return correlationDataDict,lagDataDict

def process_dataset(dataSet, noOfChannels, path_to_files, min_sample_range = 1000, max_sample_range = 3000):
    """
    Provide information about the dataset to be processed. The information given is no. of channels, .csv file having
    information about the dataset and the user can define the range of samples that have to be considered for finding similarity between two signals.
    :param dataSet: dataFrame
    :param noOfChannels: int
    :param path_to_files: str
    :param min_sample_range: int
    :param max_sample_range: int
    :return: dataFrame
    """

    # Determine the number of sequeces offered in the given data structure. Each sequence is of X seconds.
    totalSequence = int(dataSet.shape[0]/noOfChannels)

    # Create the list of indexes
    indexList = [i for i in range(0,dataSet.shape[0],noOfChannels)]

    list_of_correlation = []
    list_of_lag = []

    # Go through each index on the dataset and select all the channels
    for index in indexList:
        # Get the subset of the dataset
        subsetDataFrame = dataSet.iloc[index : index + noOfChannels]
        print(f"Size: {subsetDataFrame.shape}")

        # Find the point with max intensity
        idMaxSample = subsetDataFrame["Max_intensity"].idxmax()
        # From the id get the sample point
        sampleTiming = dataSet.iloc[idMaxSample]["Max_sample_timing"]
        # fine channel of data
        focalChannel = dataSet.iloc[idMaxSample]["Channel"]

        #list of files
        files = subsetDataFrame["Filename"].tolist()

        dataDict, lagDict = find_correlation_points(files, sampleTiming, focalChannel, path_to_files,  min_sample_range, max_sample_range)
        listOfCorrVal = list(dataDict.values())
        list_of_correlation = list_of_correlation + listOfCorrVal

        listOfLagVal = list(lagDict.values())
        list_of_lag = list_of_lag + listOfLagVal

        print(f" lag values :{len(list_of_lag)} - lag values in the session : {len(listOfLagVal)}")

    # Find max intensity value and corresponding sample value (index)
    dataSet["Correlation"] = list_of_correlation
    dataSet["Lag"] = list_of_lag

    # Define sample range around the sample value
    return dataSet



if __name__ == '__main__':
    """
    The file process the data given for the dataset. The structure of dataset defines the processing sequence. 
    We provide two ways of processing the data. 
    """
    starlingData = False
    ## Format one : Dir\Date\time
    if starlingData == True:
        path = "X:\\Nora_Data\\For Barn Methods\\Starling_Audio"

        # Define directories to go through
        folderNames = ["8th", "9th", "10th"]
        hours = ["11", "12", "13"]
        mins = ["00", "15", "30", "45"]

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
                        pathList.append(path_with_date_hour_min)
                        print(path_with_date_hour_min)

        for path in pathList:
            path_database = os.path.join(path, "updated_dataBase.csv")
            if os.path.exists(path_database):
                print(f'*.csv exists : {path_database} ')
                dataSet = pd.read_csv(path_database)
                noOfChannels = 23
                updated_dataset = process_dataset(dataSet, noOfChannels, path)
                final_file = os.path.join(path, "correlation.csv")
                updated_dataset.to_csv(final_file, index=False)
            else:
                print(f" *.csv does not exist: {path_database}")
    # Format 2 : Dir \\ Name
    else:
        path = "X:\\Mate_Data\\MALTA_Recordings\\2021_05_11"

        folderNames = ["batlure", "barnoutline", "batluremoving", "birdcalls", "mobile", "mobile2", "static"]

        # Create a list of directories from the defined directory names
        pathList = []
        for dir in folderNames:
            path_with_dir = os.path.join(path, dir)
            # Add only those directories that exist
            if os.path.exists(path_with_dir):
                pathList.append(path_with_dir)
                print(path_with_dir)

        for path in pathList:
            path_database = os.path.join(path, "updated_dataBase.csv")
            if os.path.exists(path_database):
                print(f'*.csv exists : {path_database} ')
                dataSet = pd.read_csv(path_database)
                noOfChannels = 30
                updated_dataset = process_dataset(dataSet, noOfChannels, path,  min_sample_range = 1000*3, max_sample_range = 3000*3)
                final_file = os.path.join(path, "correlation.csv")
                updated_dataset.to_csv(final_file, index=False)
            else:
                print(f" *.csv does not exist: {path_database}")
