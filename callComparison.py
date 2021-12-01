import os
import pandas as pd

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
def process_subset(path_to_files,data_subset):
    # find max intensity

    max_intensity_id = data_subset["Max_intensity"].idxmax()
    sample_number = data_subset["Max_sample_timing"].loc[max_intensity_id]
    file_name = data_subset["Filename"].loc[max_intensity_id]

    return file_name, sample_number

if __name__ == "__main__":
    """
    """
    path_to_files = "D:\\Barn Stuff\\AudioSamples"

    path_to_files_testing = "D:\\Barn Stuff\\AudioSamples"

    path_database = os.path.join(path_to_files_testing,"database.csv")
    startHour = 11
    startMin = 15
    endMin = 15
    seconds = [i for i in range(0,10,5)]

    dataBase = read_csv(path_database)

    for sec in seconds:
        query_str = get_query_value(startHour,startMin,sec)
        print(query_str)
        data_subset = grab_data_for_given_query(dataBase, query_str)
        if data_subset.empty:
            print("No data found for the query")
            break
        file_name, sample_number = process_subset(path_to_files,data_subset)

        print(data_subset.shape)

    print("File read")

    # Load file frome Nora


    # Load file prepared by our algorithm
    # Combine data from all the files to have one single big file

    # For each file in Nora's calls, find matching file and read stats


    # Read file name and call start times

