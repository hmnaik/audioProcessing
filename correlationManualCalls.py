
import os
import pandas as pd
import librosa
import numpy

def getSampleData(file, minRange, maxRange):
    #work out padding
    samples, Fs = librosa.load(file, sr=None)
    samples = samples[minRange:maxRange]
    print(f"Size: {len(samples)}")
    return samples

def find_correlation_points(soundFiles, sampleTiming, focalChannel, path_to_files):
    print("Temp")
    dataDict = {}

    # Find sample values for all the files
    focalFile = [i for i in soundFiles if str(focalChannel) in i ]

    min_sample_range = 1000
    max_sample_range = 3000
    focalFile_path = os.path.join(path_to_files, focalFile[0])
    dataOnFocalFile = getSampleData(focalFile_path, sampleTiming-min_sample_range, sampleTiming+max_sample_range)

    for file in soundFiles:
        # Select the file that is not focal file
        if file == focalFile:
            print("File")
            correlation = 0
            dataDict[file] = correlation
        else:
            queryFilePath = os.path.join(path_to_files, file)
            dataOnQueryFile = getSampleData(queryFilePath, sampleTiming-min_sample_range, sampleTiming+max_sample_range)
            #signal.correlate(dataOnFocalFile, dataOnQueryFile, mode="full", method= "auto")
            corr_values = numpy.correlate(dataOnFocalFile,dataOnQueryFile)
            print(f"Corrleation: {corr_values}")
            dataDict[file] = corr_values

    return dataDict

def process_dataset(dataSet, noOfChannels, path_to_files):

    print("Information")
    # Take subset of first 23 channels
    totalSequence = int(dataSet.shape[0]/noOfChannels)

    # Create the list of indexes
    indexList = [i for i in range(0,dataSet.shape[0],totalSequence)]

    # Go through each index on the dataset and select all the channels
    for index in indexList:
        # Get the subset of the dataset
        subsetDataFrame = dataSet.iloc[index : index + noOfChannels]
        # Find the point with max intensity
        idMaxSample = subsetDataFrame["Max_intensity"].idxmax()
        # From the id get the sample point
        sampleTiming = dataSet.iloc[idMaxSample]["Max_sample_timing"]
        # fine channel of data
        focalChannel = dataSet.iloc[idMaxSample]["Channel"]

        #list of files
        files = subsetDataFrame["Filename"].tolist()
        min_sample_range = 1000
        max_sample_range = 3000

        dataDict = find_correlation_points(files, sampleTiming, focalChannel, path_to_files)

    # Find max intensity value and corresponding sample value (index)

    # Define sample range around the sample value

    # Get sample value of all such sound files and file correlation factor with those files

    # Save focal value, correlation value and the time lag

    # Write the information in the new file




if __name__ == '__main__':
    """
    """

    path_to_files = "D:\\Barn Stuff\\AudioSamples"
    path_database = os.path.join(path_to_files, "updated_dataBase.csv")

    dataSet = pd.read_csv(path_database)
    noOfChannels = 23
    process_dataset(dataSet, noOfChannels, path_to_files)