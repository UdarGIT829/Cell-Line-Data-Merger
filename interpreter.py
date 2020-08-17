import csv
import merge_sheets_to_master as msm
from pathlib import Path
from header import *
from merge_sheets_to_master import *


#define input file based on merging program

inputFilename = msm.merge_to_csv()

#input file as List of rows (2d matrix)
structure = list()
with open(inputFilename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        structure.append(row)

print(len(structure))
#flag for set of plates (1 control, multiple treatment plates); begin as false
inControlPlate = False
inTreatmentPlate = False
activeJob = None
jobList = list()
for row in structure:
    if len(row) != 0:
        if len(row[0]) != 0:
            if "Name:" in row[0]:
                name = str(row[0][6:])
            elif "SET UP DATE:" in row[0]:
                date = str(row[0][12:])
            #Ack Control Plate
            elif "CONTROL PLATES:" in row[0]:
                #if there was a job being entered into, save it into the list of jobs
                if activeJob != None:
                    print("==========")
                    print("Saved JOB!")
                    print("==========")
                    jobList.append(activeJob)
                else:
                    activeJob = job(name,date)
                inControlPlate = True; inTreatmentPlate = False
                dayList = list()
                #print("BEGIN CONTROL")
            elif "TREATMENT PLATES:" in row[0]:
                #Save last control plate here, as it is finished being read
                thisControl = control_plate(dayList[0], dayList[1], controlCellLines)
                activeJob.setControl( thisControl )
                #Save last treatment plate here, same reason
                try:
                    activeJob.setTreatments(thisTreatmentPlate)
                except NameError:
                    pass
                #Establish new treatement plate, with empty list
                thisTreatmentPlate = treatment_plate( list() )

                inControlPlate = False; inTreatmentPlate = True
                positionList = list()
                for column in range(2,len(row)):
                    if row[column]:
                        positionList.append( row[column] )
                    column += 1
                #print("TREATMENT POS's: ",positionList)
            elif inControlPlate:
                
                dayNumber = int(row[0][3])
                dayBarcode = row[1]
                dayList.append(dayBarcode)
                controlCellLines = dict()
                for column in range( 2,len(row) ):
                    controlCellLines[row[column]] = column-1
                print("\t", controlCellLines)
                #print("Searching for 'Cell Line 1' in Dict: ", controlCellLines.get("Cell Line 1") )

            elif inTreatmentPlate:
                drugName = row[0]
                treatmentBarcode = row[1]
                drugCellLine_List = list()
                for column in range(2,len(row)):
                    if row[column]:
                        Tposition = positionList[column-2]
                        Cposition = activeJob.control.cellLines.get(row[column])
                        cellLineData = row[column]
                        drugCellLine_List.append( (Cposition,Tposition,cellLineData) )
                    column += 1
                print(drugCellLine_List)
                thisDrugTreatment = drug_treatment(drugName,treatmentBarcode,drugCellLine_List)
                thisTreatmentPlate.addToTreatments(thisDrugTreatment)
                
needHeader = True
for singularjob in jobList:
    finalcsvName = modified_to_csv( singularjob.asOutput(),needHeader )
    needHeader = False
    print("Exported to: ", finalcsvName)
csv_to_master(finalcsvName)
#loop to find Treatment or drug plates until: row[0] == False to detect if string is empty

#Control Plates are <Day N-BC, CellLine1, CellLine2, CellLine3, 4, 5, 6, 7, 8 > Total 9cells, one name
