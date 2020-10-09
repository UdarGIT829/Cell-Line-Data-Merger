"""
Made by: Viraat Udar

Latest updates can be found at: https://github.com/UdarGIT829/Cell-Line-Data-Merger


"""

from merge_sheets_to_master import *
from pathlib import Path
import platform

ignoreList = list( ("~", "master.xlsx", "master.csv") )

posixFlag = False
if "Linux" in platform.platform():
    print("Expecting Posix FS, using log file output...")
    posixFlag = True

if posixFlag:
    #Clear old log
    clearLog("log.txt")

    log_file = logData()

#merge xlsx files, with all sheets to csv
inputFilenames = merge_to_csv()

#store data from csv
needsHeader = True
for inputFilename in inputFilenames:
    tempJobList = csv_to_data(inputFilename)
    print("\n",inputFilename ,"processed!\n")
    for day in tempJobList:
        print("For: ",inputFilename,"\n\t",day,"\n")
        modified_to_csv(day.asOutput(), needsHeader)
        needsHeader = False

#Check data before export
finalCSV = final_data_checker("tempMaster.csv")

#export data to xlsx using given format
csv_to_master(finalCSV)

clean_temp_files()

if posixFlag:
    closeLog(log_file)
