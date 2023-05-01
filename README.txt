The code is divided into three parts. The part 1 is the code to process the acousic files in a batch. The input of the acoustic file depends on the recording style and data storage format. The acoustic files are processed and stored in .csv files for further processing. 

The data given for case study A can be used directly. 

-- Part 1

Automated processing for the data recorded by microphnes. 
1. callIdentifier.py
The file processes audio files given in a particular directory. These files usually contain sound recording of all microphones. This script will process all audio files and for each time duration finds the 
channel that records maximum intensity of sound. This channel is our first approximation to locate the sound source. We record intensity and the time of the sound w.r.t the recording file.
output : database.csv

2. callComparison.py
The script, collects timing and intensity of sound in each clip. The file from callIdentifier.py is processed for each time duration. We identify the channel that records the loudes sound among all channels. 
Based on the timing of the loudest sound, we process all audio files only for time window that is closer to loudest sound. Then we pick the loudest sound in this time window. This allows us to identify recording of a
single sound from all channels. We assume that it is easy to identify loudest sound.
output : updated_database.csv

3. correlateAutomatedCalls.py
The scipt will take results from callComparison.py and compute cross correlation between the files. This allows us to find the time delay between the focal signal and all the other signals. 
This data is finally used to triangular the sound source to get 3D location of the sound.
output : correlation.csv

-- Separate file for manually annotated data and processing it. 
Manual processing for the data gathered by manual processing.
1. readTextFile.py 
The text file contains name of the .wav file that is manually annotated for bird calls, along with the timing. 
The script creates .csv file from the given file for computing cross correlation. 
The workflow differs with the automated processing in a way tha callIdentifier.py is skipped. The callComparison.py is 
used with the given annotations. 

2. processManualCalls.py
The script creates cross correlation from the annotated data. The processing is same as the automated method explained earlier. 

-- Part 2
Use the correlation data to triangulate sound location and then further match the location with vicon. 

1. CORR_directcalc_corrweight_iterPer1_nofitv.py

* Process final results to get combined audio files. Get Optimisation for x,y,z and timing for the sound source based on time difference of arrival (tdoa) from the mic data
--> RUN CORR_directcalc_corrweight_iterPer1_nofitv.py
--> python CORR_directcalc_corrweight_iterPer1_nofitv.py correlationbased/correlation_11-15.csv >OUTcorr_11-15

# OR use the script run and run_manual
# Note that the column number was different for the automated and the manual files

Concatenate output files using cat
CHECK the Goodness of the Fit, (actually the residual, the smaller the better, which is the  sum of the square difference
Ignore those localisation from further analysis where:
- any parameter value is on or very close to the range of the set interval for the fitting
- any parameter value is at the initial value of the optimisation
- where the remaining residuals are still high

Output: OUTiter2_all17_newAll_6.xlsx
save gettracks... into csv,


2. getviconlocation_and_distance.py

# Get VICON data for the same time instances
RUN getviconlocation_and_distance.py

#python getviconlocation_and_distance.py gettracks_manualForDist.csv >OUTloc_manual

Input files: gettracks_7th.csv, gettracks_8th.csv, gettracks_9th.csv, gettracks_10th.csv, gettracks_manualForDist.csv
output: OUTloc_7th, OUTloc_8th, OUTloc_9th, OUTloc10th, OUTloc_manual

concatenate using cat. Calc. distances in Excel (for simplicity). Get if ID can be assigned based on distance of the sound from closest and from the second closet individual's backpack marker pattern (Possible future improvement: use backpack orientation (quaternions) to have a better estimate for the location of the head. Pro: more accurate for vocalisation. Con: maybe less accurate due to marker pattern false recognition flips; less accurate for sounds other then calls

Final result: OUTlocID_alldays1.csv, OUTlocID_manual1.csv, OUTloc_all_12.xls
