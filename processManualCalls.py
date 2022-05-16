'''
This files is designed to read the manually annotated file created by Nora.
We read the call timings and find the audio signal from corresponding audio of the corresponding channel.
Then we extract samples from recording of the other channels at the same time to perform cross correlation.
'''

# Author : Hemal Naik

import math
import csv
import pandas as pd
import os
import glob
from scipy import signal
import numpy as np
import librosa

def getSampleData(file, minRange, maxRange):
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

    # Maximum intensity among samples
    maxAmp = max(samples)
    # The implementation below is to avoid a bug, that if any similar value exist outside the range then we would not really get the right index
    selected_sample_values = list(samples)
    sampleNoMax = selected_sample_values.index(maxAmp)
    sampleNoMax = sampleNoMax + minRange

    return samples, maxAmp, sampleNoMax

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

def process_audio( soundFiles , sampleTiming , focalFile, path_to_files):
    correlationDataDict = {}
    lagDataDict = {}

    sampleLocationsMaxAmp = {}
    ampValues = {}

    #focual_index = soundFiles.index(focalFile)

    # Find sample values for all the files
    #focalFile = [i for i in soundFiles if str(focalChannel) in i]

    min_sample_range = 1000
    max_sample_range = 3000

    focalFile_path = os.path.join(path_to_files, focalFile)
    dataOnFocalFile, maxAmp, sampleNo = getSampleData(focalFile_path, sampleTiming - min_sample_range, sampleTiming + max_sample_range)

    for file in soundFiles:
        # Select the file that is not focal file
        if str(focalFile) in file:
            correlation = 0
            lagDataDict[file] = 0
            correlationDataDict[file] = correlation
            ampValues[file] = maxAmp
            sampleLocationsMaxAmp[file] = sampleNo
        else:
            queryFilePath = os.path.join(path_to_files, file)
            dataOnQueryFile, maxAmp, sampleNo = getSampleData(queryFilePath, sampleTiming - min_sample_range,
                                            sampleTiming + max_sample_range)

            ampValues[file] = maxAmp
            sampleLocationsMaxAmp[file] = sampleNo

            # Find correlation
            corr_values = signal.correlate(dataOnQueryFile, dataOnFocalFile, mode="full", method="auto")
            maxCorr = np.max(corr_values)

            # find lags
            lags = signal.correlation_lags(len(dataOnFocalFile), len(dataOnQueryFile), mode="full")
            lag = lags[np.argmax(corr_values)]

            # Save value to dictionary
            correlationDataDict[file] = maxCorr
            lagDataDict[file] = lag


            # Plotting values
            # corr_values = numpy.correlate(dataOnFocalFile,dataOnQueryFile)
            # print(f"Corrleation: {corr_values}")
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

    return correlationDataDict, lagDataDict, sampleLocationsMaxAmp, ampValues

def findInfoFromName(audioFileName):
        dict = {}
        audioFileName = os.path.basename(audioFileName)
        sections = audioFileName.split("_")
        channelSection = sections[1].split("Chan")
        dateSection = sections[2].split("-")
        timeSection = sections[3].split("-")

        dict["Filename"] = audioFileName
        dict["Channel"] = channelSection[1]
        dict["Year"] = dateSection[0]
        dict["Month"] = dateSection[1]
        dict["Day"] = dateSection[2]
        dict["Hour"] = timeSection[0]
        dict["Minute"] = timeSection[1]
        dict["Seconds_5"] = timeSection[2]

        return dict

def write_data_to_csv(csv_file_path, file_names, correlation_dict, lag_dict, sampleLocations, ampValues, manual_sample_no):
    data = pd.read_csv(csv_file_path)

    #columns = data.columns.tolist()
    dataDict = {}
    # Add data for all files
    for file in file_names:
        dict = findInfoFromName(file)
        dataDict.update(dict)
        dataDict["Max_intensity"] = ampValues[file]
        dataDict["Max_sample_timing"] = sampleLocations[file]
        dataDict["Manual_sample_no"] = manual_sample_no
        dataDict["Correlation"] = correlation_dict[file]
        dataDict["Lag"] = lag_dict[file]
        data = data.append(dataDict, ignore_index= True)

    data.to_csv(csv_file_path, index= False)

#Find the right folder for the audio files
def process_data(dataFrame, audio_file_path, csv_file_path):
    fifteenTime = dataFrame["fifteentime"].tolist()
    time_section = dataFrame["timesection"].tolist()
    file_names = dataFrame["soundFileName"].tolist()
    manual_sample_no = 0

    manualSampleDict = {}

    for iterator in range(0,len(fifteenTime)):
        hrs = str(time_section[iterator]).split("_")[0]
        mins = str(time_section[iterator]).split("_")[1]
        folder_name = os.path.join(audio_file_path, hrs+"-"+mins)
        print(f'Directory : {folder_name}')
        file_name = os.path.join(folder_name, str(file_names[iterator]))
        if os.path.exists(file_name):
            print(f'Processing audio file: {file_name}')
            callTime, manual_sample_no = find_sampleno_from_call_time(fifteenTime[iterator])

        # Seprate the query text i.e. time --> Hrs-Min-Sec
        queryText = str(file_names[iterator]).split("_")[3]
        # Find sound files with same time stamp
        sound_files_in_folder = glob.glob(os.path.join(folder_name,"*.wav")) # Returns file names with full path
        matching_files = [i for i in sound_files_in_folder if queryText in i] # Returns file names with required time stamp

        correlation_dict, lag_dict, sampleLocations, ampValues = process_audio(matching_files, manual_sample_no, file_names[iterator], folder_name)

        write_data_to_csv(csv_file_path, matching_files, correlation_dict, lag_dict, sampleLocations, ampValues, manual_sample_no)
        #dataDict[file_names[iterator]] = (correlation_dict, lag_dict)

    return True

def prepare_csv_file(path, filename):

    csvFilePath = os.path.join(path , filename)
    print(f'Csv Path:{csvFilePath}')

    # Create handler for csv storage file and write header
    csvFileHandler = open(csvFilePath, "w", newline="")
    csvWriter = csv.writer(csvFileHandler, delimiter=",")
    header = ["Filename", "Channel", "Year", "Month", "Day", "Hour", "Minute", "Seconds_5", "Max_intensity",
              "Max_sample_timing","Manual_sample_no", "Correlation", "Lag"]
    csvWriter.writerow(header)

    # close the file
    csvFileHandler.close()

    return csvFilePath

if __name__ == '__main__':
    """
    """
    name = "X:\\HemalData\\Software Dev\\audioProcessing\\trial1_Chan14_2019-12-09_11-15-00to13-00_OnlyVerrifiedCalls_modified.csv"
    dataFrame = pd.read_csv(name)
    audio_file_path = "X:\\Nora_Data\\For Barn Methods\\Starling_Audio"
    # filename for storing data
    csv_file_name = "manual_corr.csv"
    csv_file_path = prepare_csv_file(audio_file_path, csv_file_name)
    #
    process_data(dataFrame, audio_file_path, csv_file_path)





