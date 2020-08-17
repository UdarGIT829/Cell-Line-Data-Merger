import merge_sheets_to_master as msm
from pathlib import Path
from header import *

#merge xlsx files, with all sheets to csv
inputFilename = msm.merge_to_csv()

#store data from csv
jobList = csv_to_data(inputFilename)

#export data to xlsx using given format
data_to_xlsx(jobList)     
