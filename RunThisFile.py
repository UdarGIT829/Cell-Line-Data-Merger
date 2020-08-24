from merge_sheets_to_master import *
from pathlib import Path

ignoreList = list( ("~", "master.xlsx", "master.csv") )

#merge xlsx files, with all sheets to csv
inputFilenames = merge_to_csv_new()

#store data from csv
needsHeader = True
for inputFilename in inputFilenames:
    tempJobList = csv_to_data_new(inputFilename)
    for day in tempJobList:
        print("For: ",inputFilename,"\n\t",day)
        modified_to_csv(day.asOutput(), needsHeader)
        needsHeader = False

#export data to xlsx using given format
csv_to_master("tempMaster.csv")

clean_temp_files()