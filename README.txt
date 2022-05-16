# Get Optimisation for x,y,z and timing for the sound source based on time difference of arrival (tdoa) from the mic data
# RUN CORR_directcalc_corrweight_iterPer1_nofitv.py
python CORR_directcalc_corrweight_iterPer1_nofitv.py correlationbased/correlation_11-15.csv >OUTcorr_11-15
# 
# OR use the script run and run_manual
# Note that the column number was different for the automated and the manual files
#
# Concatenate output files using cat
#
# CHECK the Goodness of the Fit, (actually the residual, the smaller the better, which is the  sum of the square difference
# Ignore those localisation from further analysis where:
# - any parameter value is on or very close to the range of the set interval for the fitting
# - any parameter value is at the initial value of the optimisation
# - where the remaining residuals are still high
#
# Result: OUTiter2_all17_newAll_6.xlsx
# save gettracks... into csv,
#
# Get VICON data for the same time instances
# RUN getviconlocation_and_distance.py
#
python getviconlocation_and_distance.py gettracks_manualForDist.csv >OUTloc_manual
#
# Input files> gettracks_7th.csv, gettracks_8th.csv, gettracks_9th.csv, gettracks_10th.csv, gettracks_manualForDist.csv
# Resulting OUTput files
# (OUTloc_7th, OUTloc_8th, OUTloc_9th, OUTloc10th, OUTloc_manual
#
# concatenate using cat. Calc. distances in Excel (for simplicity)
# Get if ID can be assigned based on distance of the sound from closest and from the second closet individual's backpack marker pattern
#
# (Possible future improvement: use backpack orientation (quaternions) to have a better estimate for the location of the head. Pro: more accurate for vocalisation. Con: maybe less accurate due to marker pattern false recognition flips; less accurate for sounds other then calls
#
# Resulting data files:
# OUTlocID_alldays1.csv, OUTlocID_manual1.csv
# OUTloc_all_12.xls