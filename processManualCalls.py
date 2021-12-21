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

    # Fine sample values
    maxAmp = max(samples)

    # The implementation below is to avoid a bug, that if any similar value exist outside the range then we would not really get the right index
    selected_sample_values = list(samples)
    sampleNo = selected_sample_values.index(maxAmp)
    sampleNo = sampleNo + maxRange

    return samples, maxAmp, sampleNo

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

def process_audio( soundFiles ,  sampleTiming , focalFile, path_to_files):
    correlationDataDict = {}
    lagDataDict = {}

    sampleLocations = {}
    ampValues = {}

    print(f"List of sound files:{soundFiles} ")
    print(f"Focal file: {focalFile}")

    #focual_index = soundFiles.index(focalFile)

    # Find sample values for all the files
    #focalFile = [i for i in soundFiles if str(focalChannel) in i]

    min_sample_range = 1000
    max_sample_range = 3000

    focalFile_path = os.path.join(path_to_files, focalFile[0])
    #dataOnFocalFile, maxAmp, sampleNo = getSampleData(focalFile_path, sampleTiming - min_sample_range, sampleTiming + max_sample_range)

    for file in soundFiles:
        # Select the file that is not focal file
        if file == focalFile:
            # print("File")
            correlation = 0
            correlationDataDict[file] = correlation
            #ampValues[file] = maxAmp
            #sampleLocations[file] = sampleNo
        else:
            queryFilePath = os.path.join(path_to_files, file)
            #dataOnQueryFile, maxAmp, sampleNo = getSampleData(queryFilePath, sampleTiming - min_sample_range,
                                           # sampleTiming + max_sample_range)

            #ampValues[file] = maxAmp
            #sampleLocations[file] = sampleNo

            # Find correlation
            #corr_values = signal.correlate(dataOnQueryFile, dataOnFocalFile, mode="full", method="auto")
            #maxCorr = np.max(corr_values)

            # find lags
            #lags = signal.correlation_lags(len(dataOnFocalFile), len(dataOnQueryFile), mode="full")
            #lag = lags[np.argmax(corr_values)]

            # Save value to dictionary
            # correlationDataDict[file] = maxCorr
            # lagDataDict[file] = lag


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

    return correlationDataDict, lagDataDict, sampleLocations, ampValues

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

def write_data_to_csv(csv_file_name, file_name, correlation_dict, lag_dict, sampleLocations, ampValues):
    print("Temp values")



#Find the right folder for the audio files
def process_data(dataFrame, audio_file_path, csv_file_name):
    fifteenTime = dataFrame["fifteentime"].tolist()
    time_section = dataFrame["timesection"].tolist()
    file_names = dataFrame["soundfilename"].tolist()
    sample_no = 0

    dataDict = {}

    for iterator in range(0,len(fifteenTime)):
        hrs = str(time_section[iterator]).split("_")[0]
        mins = str(time_section[iterator]).split("_")[1]
        folder_name = os.path.join(audio_file_path, hrs+"-"+mins)
        print(f'Directory : {folder_name}')
        file_name = os.path.join(folder_name, str(file_names[iterator]))
        if os.path.exists(file_name):
            print(f'Processing audio file: {file_name}')
            callTime, sample_no = find_sampleno_from_call_time(fifteenTime[iterator])

        # Seprate the query text i.e. time --> Hrs-Min-Sec
        queryText = str(file_names[iterator]).split("_")[3]
        # Find sound files with same time stamp
        sound_files_in_folder = glob.glob(os.path.join(folder_name,"*.wav"))
        matching_files = [i for i in sound_files_in_folder if queryText in i]

        correlation_dict, lag_dict, sampleLocations, ampValues = process_audio(matching_files, sample_no, fifteenTime[iterator], folder_name)

        

        write_data_to_csv(csv_file_name, file_names[iterator], correlation_dict, lag_dict, sampleLocations, ampValues)
        #dataDict[file_names[iterator]] = (correlation_dict, lag_dict)

    return dataDict

def prepare_csv_file(path, filename):

    csvFilePath = os.path.join(path , filename)
    print(f'Csv Path:{csvFilePath}')

    # Create handler for csv storage file and write header
    csvFileHandler = open(csvFilePath, "w", newline="")
    csvWriter = csv.writer(csvFileHandler, delimiter=",")
    header = ["Filename", "Channel", "Year", "Month", "Day", "Hour", "Minute", "Seconds_5", "Max_intensity",
              "Max_sample_timing", "Manual_sample_timing", "Correlation", "Lag"]
    csvWriter.writerow(header)

    # close the file
    csvFileHandler.close()

if __name__ == '__main__':
    """
    """
    name = "D:\\Barn Stuff\\VerificationFile\\trial1_Chan14_2019-12-09_11-15-00to13-00_OnlyVerrifiedCalls_modified.csv"
    dataFrame = pd.read_csv(name)
    audio_file_path = "D:\\Barn Stuff\\AudioSamples"
    # filename for storing data
    csv_file_name = "manual_corr.csv"
    prepare_csv_file(audio_file_path, csv_file_name)
    #
    process_data(dataFrame, audio_file_path, csv_file_name)





