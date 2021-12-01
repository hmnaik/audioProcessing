import os
import pandas as pd
import librosa
#
def read_csv(file_name):
    """
    :param file_name:
    :return:
    """
    dataBase = pd.read_csv(file_name)
    return dataBase

#
def get_query_value(hour,min,seconds):
    # Convert all values to string
    hour_str = str(hour)
    min_str = str(min)
    if min < 10:
        min_str = "0" + min_str
    sec_str = str(seconds)
    if seconds < 10:
        sec_str = "0" + sec_str
    # Get query value
    query = hour_str + "-" + min_str + "-" + sec_str

    return query
#
def grab_data_for_given_query(dataBase,query_string):

    # This subset should have information about all the channels in the given time series
    subSet = dataBase[dataBase["Filename"].str.contains(query_string)]
    return subSet

#def update_values(subset_database):
def process_subset(data_subset):
    # find max intensity

    max_intensity_id = data_subset["Max_intensity"].idxmax()
    sample_number = data_subset["Max_sample_timing"].loc[max_intensity_id]
    file_name = data_subset["Filename"].loc[max_intensity_id]

    return file_name, sample_number


def findMaxValues(path_to_files,file_names,sample_min, sample_max):

    sample_locations = []
    amp_values = []
    for file in file_names:
        # Go thought all the files
        audio_file_path = os.path.join(path_to_files,file)
        fn_wav = str(audio_file_path)

        x, Fs = librosa.load(fn_wav, sr=None)
        if sample_max > 500000:
            sample_max = 500000

        # Fine sample values
        selected_sample_values = x[sample_min:sample_max]
        maxAmp = max(selected_sample_values)

        # The implementation below is to avoid a bug, that if any similar value exist outside the range then we would not really get the right index
        selected_sample_values = list(selected_sample_values)
        sampleNo = selected_sample_values.index(maxAmp)
        sampleNo = sampleNo + sample_min

        # Create a list of the new values
        sample_locations.append(sampleNo)
        amp_values.append(maxAmp)

    return sample_locations, amp_values


if __name__ == "__main__":
    """
    """
    path_to_files = "D:\\Barn Stuff\\AudioSamples"

    path_to_files_testing = "D:\\Barn Stuff\\AudioSamples"

    path_database = os.path.join(path_to_files_testing,"database.csv")
    startHour = 11
    startMin = 15
    endMin = 15
    seconds = [i for i in range(0,60,5)]

    dataBase = read_csv(path_database)

    updatedDataBase = []

    for sec in seconds:
        query_str = get_query_value(startHour,startMin,sec)
        print(query_str)
        data_subset = grab_data_for_given_query(dataBase.copy(), query_str)

        if data_subset.empty:
            print("No data found for the query")
            break
        max_file_name, sample_number = process_subset(data_subset.copy())
        # All file names
        file_names = data_subset["Filename"]

        sample_locations, amp_values = findMaxValues(path_to_files, file_names, sample_number-1000, sample_number+3000)
        print(f'Max sample:{sample_number}')
        print(f"Sameple range : {sample_number-1000} - {sample_number+3000}")
        print(f'Old Intensity: {data_subset["Max_intensity"].tolist()}\n New Val: {amp_values}') # :{data_subset["Max_sample_timing"]}
        print(f'Old Sample Number : {data_subset["Max_sample_timing"].tolist()} \n New value: {sample_locations}')

        data_subset["Max_intensity"] = amp_values
        data_subset["Max_sample_timing"] = sample_locations

        updatedDataBase.append(data_subset)

    final_dataset = pd.concat(updatedDataBase)
    newFileName = os.path.join(path_to_files, "updated_dataBase.csv")
    final_dataset.to_csv(newFileName, index= False)
