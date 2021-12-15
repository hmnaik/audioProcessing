
import os
import pandas as pd
import librosa
import numpy as np
from scipy import signal
from matplotlib import pyplot as plt

def getSampleData(file, minRange, maxRange):
    #work out padding
    samples, Fs = librosa.load(file, sr=None)
    samples = samples[minRange:maxRange]
    #print(f"Size: {len(samples)}")
    return samples

def find_correlation_points(soundFiles, sampleTiming, focalChannel, path_to_files):
    correlationDataDict = {}
    lagDataDict = {}

    # Find sample values for all the files
    focalFile = [i for i in soundFiles if str(focalChannel) in i ]

    min_sample_range = 1000
    max_sample_range = 3000
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

            print("Waiting")

    return correlationDataDict,lagDataDict

def process_dataset(dataSet, noOfChannels, path_to_files):

    # Take subset of first 23 channels
    totalSequence = int(dataSet.shape[0]/noOfChannels)

    # Create the list of indexes
    indexList = [i for i in range(0,dataSet.shape[0],noOfChannels)]

    list_of_correlation = []
    list_of_lag = []

    # Go through each index on the dataset and select all the channels
    for index in indexList:
        print(f"index: {index}")
        if index == 528:
            print("Now")
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
        # min_sample_range = 1000
        # max_sample_range = 3000

        dataDict, lagDict = find_correlation_points(files, sampleTiming, focalChannel, path_to_files)
        listOfCorrVal = list(dataDict.values())
        list_of_correlation = list_of_correlation + listOfCorrVal
        #print(len(list_of_correlation))

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
    """

    path_to_files = "D:\\Barn Stuff\\AudioSamples"
    path_database = os.path.join(path_to_files, "updated_dataBase.csv")

    dataSet = pd.read_csv(path_database)
    noOfChannels = 23
    updated_dataset = process_dataset(dataSet, noOfChannels, path_to_files)
    final_file = os.path.join(path_to_files, "correlation.csv")
    updated_dataset.to_csv(final_file, index = False)