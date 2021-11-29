import math
import csv


def find_time_stamp(fifteentime):
    mins = math.floor( fifteentime / 60)
    totalSecs = math.floor(fifteentime - (mins * 60))
    seconds = math.floor(totalSecs/5)*5
    return mins, seconds

def read_File(filename):
    filename_without_extension = filename.split(".txt")[0]
    filename_with_extension = filename_without_extension + "_modified" + ".txt"
    csvFileName = filename_without_extension + "_modified" + ".csv"

    csvFileHandler = open(csvFileName,'w', newline= "")
    csvWriter = csv.writer(csvFileHandler, delimiter = ",")
    #
    dataFile = open(filename_with_extension, "w+")
    # For identification of file names
    wavFilePrefix = "trial1_Chan14_2019-12-09_"
    wavFileSuffix = "_ADC05000mV_00dB.wav"
    lineCount = 0

    with open(filename) as file:
        lines = file.readlines()
        # Go through everyline
        for line in lines:
            line = line.rstrip()
            listOfValues = line.split("\t")
            # find the lines with values (Not header and not empty lines)
            if lineCount == 0:
                listOfValues.append("soundFileName")
                csvWriter.writerow(listOfValues)

            elif len(listOfValues)>1 and lineCount != 0:
                # Find time of call within 15 min session (Mins and Seconds)
                timeOfCall = float(listOfValues[3])
                call_mins, base_seconds = find_time_stamp(timeOfCall)
                # Find the correct 15 min segment to add mins and seconds
                time_stamp = listOfValues[6].split("_")
                base_hour = int(time_stamp[0])  # Extract base hour value
                base_mins = int(time_stamp[1])  # Extract base min value
                total_mins = base_mins + call_mins
                #listOfValues.append(str(hour))
                #listOfValues.append(str(basemins + mins))
                if base_seconds < 10:
                    base_seconds = "0" + str(base_seconds)
                #listOfValues.append(str(base_seconds) )
                # Create name of the audio file
                audioFileName = wavFilePrefix + str(base_hour) + "-" + str(total_mins) + "-" + str(base_seconds) + wavFileSuffix
                listOfValues.append(audioFileName)

                # Replace time and date with actual values
                date, time = listOfValues[5].split("_")
                updatedDateTime = date + "_" + str(base_hour) + "-" + str(total_mins) + "-" + str(base_seconds)
                listOfValues[5] = updatedDateTime

                print(listOfValues)
                dataFile.write(str(listOfValues))
                dataFile.write("\n")
                # Write in CSV writer
                csvWriter.writerow(listOfValues)
            else:
                print("Error ")

            lineCount = lineCount + 1
        #
        dataFile.close()

if __name__ == '__main__':
    """
    """
    name = "D:\\Barn Stuff\\VerificationFile\\trial1_Chan14_2019-12-09_11-15-00to13-00_OnlyVerrifiedCalls.txt"
    read_File(name)