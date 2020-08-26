"""
Run the following commands to install required libraries:

pip3 install xlrd

pip3 install xlsxwriter

if that doesnt work, try adding a -user to the end like so (but only if it says so in the error):

pip3 install xlsxwriter --user
"""
import xlrd
from xlsxwriter.workbook import Workbook
import csv
import os
import math
from header import *

from pathlib import Path
def merge_to_csv_new():
    directory = os.path.dirname(__file__)

    temporaryCsvFileName = "tempMaster.csv"

    if os.path.exists(temporaryCsvFileName):
        print("deleting old csv")
        os.remove(temporaryCsvFileName)

    excelFiles = list()
    for path in Path(directory).rglob('*.xlsx'):
        excelFiles.append(path)

    for path in excelFiles:
        if "master.xlsx" in str(path):
            print("Ignoring master.xlsx, presumed from past run")
            excelFiles.remove(path)

    print("All files being read: ", excelFiles)
    tempNameList = list()
    for path in excelFiles:
        print( "Reading file: ", os.path.basename(path) )
        tempIdentifier = os.path.basename(path).replace(" ","")[:5]
        with xlrd.open_workbook(path) as workbook:
            nameOverride = ""
            names = workbook.sheet_names()
            sheetAmount = len(names)
            for index in range(sheetAmount):
                print("Reading sheet #: ", index+1)
                sheet = workbook.sheet_by_index(index)
                tempSheetName = tempIdentifier + "sheet" + str(index+1) + ".csv"
                tempNameList.append(tempSheetName)
                with open(tempSheetName, 'a+', newline="") as file:
                    col = csv.writer(file)
                    for row in range(sheet.nrows):
                        col.writerow(sheet.row_values(row))
            file.close()
    return(tempNameList)

def csv_to_master(csvFileName):
    workbook = Workbook('master.xlsx',{'strings_to_numbers': True,'constant_memory': True})
    worksheet = workbook.add_worksheet()
    with open(csvFileName, 'r') as file:
        rows = csv.reader(file)
        for row_index, row in enumerate(rows):
            for col_index, data in enumerate(row):
                worksheet.write(row_index, col_index, data)
    workbook.close()
    print("-------------------------------------------")
    print(" .CSV to .XLSX Conversion Successful")
    print("-------------------------------------------")

def modified_to_csv(input, header=False):
    headerText = ("TreatmentBarcode","Treatment position","Staff_ID","Cell_Line_ID","SetupDate","Drug_ID_1","Starting_Concentration_in_uM","Dilution_Factor","Day1Barcode","Day1Location","Day7Barcode","Day7Location")
    directory = os.path.dirname(__file__)

    finalCsvFileName = "tempMaster.csv"
    with open(finalCsvFileName, 'a+', newline="") as file:
        col = csv.writer(file)
        if header:
            col.writerow(headerText)
        for row in input:
            col.writerow(row)
        file.close()
    return finalCsvFileName

def incrementScanner(rowNumber, maxSize):
    if rowNumber+1 >= maxSize:
        raise Exception('End of file reached!')
    return (rowNumber+1)

def csv_to_data(inputFilename):
    initialStructure = list()
    jobList = list()
    activeJob = job()
    print("Analysing sheet csv: ",inputFilename)
#import from csv into temporary structure
    with open(inputFilename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            initialStructure.append(row)
        csvfile.close()

    Scanned_rows = list()
    structure_size = len(initialStructure)
    ignoreList = list()
    for rowNum in range( 0,structure_size ):
        thisRow = initialStructure[rowNum]
        if (len(thisRow[0]) == 0) or (rowNum in Scanned_rows) or rowNum in ignoreList:
            pass
        else:
            if "Name:" in thisRow[0]:
                tempName = thisRow[0].replace("Name: ","").replace("Name:","")
                if tempName == "":
                    print("\tMissing Name", thisRow)
                    for column in range(1,len(row)):
                        if thisRow[column] != "":
                            tempName = thisRow[column]
                if tempName == "":
                    tempName = "N/A"
                #tempName will now store name of job, if none was entered it will contain "N/A"
            else:
                #if no name row provided, assume it existed elsewhere
                print("\tno Name in row: ",thisRow)
                if "TREATMENT PLATES:" in thisRow:
                    print("\t\tUnused treatment plate detected, ignoring rest of sheet...")
                    break
                tempName = jobList[-1].Name
            
            #Establish scanner and scannerRow variables to seperately iterate through sheet without affecting for loop variable
            scanner = rowNum
            scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner]

            #Push scanner down until data is detected
            while initialStructure[scanner] == "":
                scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner]

            #Follow process as for Name with Date
            if "SET UP DATE:" in scannerRow[0]:
                tempDate = str(scannerRow[0][12:]).replace(" ", "")
                #if date was found, then scan down again
                while scannerRow[0] == "":
                    scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner]
            else:
                #if date not found, scanner will be on Control Plate
                #set date as with name and proceed with Control Plate
                print("\tNo Date in row: ",scannerRow)
                tempDate = jobList[-1].Date
                print("Using last job's date: ", tempDate)

            #AT THIS POINT tempName, tempDate contain name and date
            #initialize job
            activeJob = job(tempName, tempDate)
            print("Job Initialized with ~ Name: ",tempName, "| Date: ", tempDate)
            #Input concentrations for Drugs
            specificDrugInfo = dict()
            while not "Starting Concentration" in scannerRow[1]:
                if "CONTROL" in scannerRow[0]:
                    break
                else:
                    scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner] 
            if "Starting Concentration" in scannerRow[1]:
                print("Successfully found starting concentration area...")
                scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner] 
                #Count amount of drugs in variable
                earlyDrugAmount = 0
                #Establish temporary dictionary to store Starting concentration and dilution factor for various drug treatments
                while ( not "CONTROL" in scannerRow[0] ) and ( len(scannerRow[0]) > 0 ):
                    earlyDrugAmount += 1
                    specificDrugInfo[ scannerRow[0] ] = ( scannerRow[1], scannerRow[2] )
                    scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner] 
                print("Starting dilution and dilution factor info: ", specificDrugInfo)

            #push scanner to next data row
            while not "CONTROL" in scannerRow[0]:
                scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner] 
            while scannerRow[0] == "":
                scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner] 
            
            #Input barcodes into dayList, cellLine-ID's will be in controlCellLines
            if "CONTROL" in scannerRow[0]:
                print("Successfully found Control Plate")
                scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner]
                #print(scannerRow)
                dayList = list()
                while "Day" in scannerRow[0]:
                    dayBarcode = scannerRow[1]
                    dayList.append(dayBarcode)
                    controlCellLines = dict()
                    for column in range(2, len(scannerRow)):
                        if scannerRow[column] != "" and not("Cell Line" in scannerRow[column]) and not("empty" in scannerRow[column]):
                            controlCellLines[scannerRow[column]] = column-1
                    scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner]
            else:
                print("\tControl not found: ", scannerRow)    
            #at this point all Control Days have been inputted, and scanner will point at next row
            #update activeJob with control plates
            tempControl = control_plate(dayList[0], dayList[1], controlCellLines)
            activeJob.setControl( tempControl )

            #push scanner to next data row
            while scannerRow[0] == "":
                scanner = incrementScanner(scanner, structure_size); scannerRow = initialStructure[scanner] 

            #scannerRow will now be on first treatment plate
            #Predict the amount of treatment plates
            treatmentColumnAmount = 0
            cellLineAmount = len(tempControl.cellLines)
            for x in range( len(scannerRow) ):
                thisCell = str(scannerRow[x])
                if not("TREATMENT PLATES:" in thisCell) and (thisCell != ""):
                    treatmentColumnAmount += 1

            drugAmount = 0
            for x in range(scanner+1, structure_size):
                if ( initialStructure[x][0] == "" ) or ( "TREATMENT PLATES:" in initialStructure[x][0] ):
                    break
                drugAmount += 1
            
            print("Drug Amount: ", drugAmount)
            print("CellLine amount: ", cellLineAmount)
            if cellLineAmount == 0:
                print("\tEmpty plate, ignoring rest of sheet...")
                break
            predicted_treatmentPlate_amount = math.ceil((cellLineAmount/8) * drugAmount)
            print("Expecting ", predicted_treatmentPlate_amount, " treatment plates.")

            treatments_data_range = list()
            for x in range(scanner, structure_size):
                if "TREATMENT PLATES:" in initialStructure[x]:
                    this_plate_range = list()
                    this_plate_range.extend(range(x, x + 1 + drugAmount))
                    treatments_data_range.append(this_plate_range)
            
            print("There are ", len(treatments_data_range), " treatment sets found in the whole sheet")
            moreThanExpected = len(treatments_data_range) - predicted_treatmentPlate_amount
            while moreThanExpected > 0:
                del treatments_data_range[-1]
                print("\t",moreThanExpected, " more treatment plates than expected, ignoring last one...")
                moreThanExpected = len(treatments_data_range) - predicted_treatmentPlate_amount

            temp_treatment_plates = list()
            for treatment_data_range in treatments_data_range:
                print("Handling treatment: ", treatment_data_range)
                temp_treatment_plate = treatment_plate()

                treatmentColumnInfo = list()
                        
                for row in treatment_data_range:
                    treatment_data = initialStructure[row]

                    while "" in treatment_data:
                        treatment_data.remove("")

                    if row == min(treatment_data_range):
                        #Treatment column info
                        treatmentColumnInfo = treatment_data
                    else:
                        #Treatment Data
                        treatment_data_length = len(treatment_data)
                        if treatment_data_length < 3:
                            print("\tIgnoring non-data row", treatment_data)
                        else:
                            tempDrugID = treatment_data[0]
                            tempDrugBC = treatment_data[1]
                            tempTreatmentCellLines = list()
                            for value in range(2, len(treatment_data) ):
                                treatmentColumnNumber = value-1
                                tempT_cellline_id = treatment_data[value]
                                tempCposition = tempControl.cellLines.get(treatment_data[value])
                                tempTposition = treatmentColumnInfo[treatmentColumnNumber]
                                tempTreatmentCellLines.append( (tempCposition,tempTposition,tempT_cellline_id) )
                                checkDrugInfo = specificDrugInfo.get(tempDrugID, "?")
                                if checkDrugInfo == "?":
                                    print("\tStarting dilution and dilution factor not found for ", tempDrugID)
                                #tempStartingDilution = specificDrugInfo.get(tempDrugID)[0]
                                #tempDilutionFactor = specificDrugInfo.get(tempDrugID)[1]
                                print(treatment_data[value]," is in control position ", tempControl.cellLines.get(treatment_data[value]), " and is in treatment position ", treatmentColumnInfo[treatmentColumnNumber] )
                            tempDrug_treatment = drug_treatment(tempDrugID,tempDrugBC,tempTreatmentCellLines, specificDrugInfo.get(tempDrugID, "?")[0], specificDrugInfo.get(tempDrugID," ?")[1] )
                            temp_treatment_plate.addToTreatments(tempDrug_treatment)
                    scanner = max(treatment_data_range)
                
                temp_treatment_plates.append(temp_treatment_plate)
            activeJob.setTreatments(temp_treatment_plates)
            jobList.append(activeJob)
            print("=================")
            print("====JOB SAVED====")
            print("=================")
                    
            ignoreList.extend(range(0,scanner+1))
            print("Ignoring processed range from: 0 to ", scanner)

    return jobList

def clean_temp_files():
    directory = os.path.dirname(__file__)

    pastFiles = list()

    for path in Path(directory).rglob('*.csv'):
        pastFiles.append(path)
    """
    for path in Path(directory).rglob('master.xlsx'):
        pastFiles.append(path)

    
    for path in pastFiles:
        if (not "sheet" in str(path)):
            pastFiles.remove(path)
    """
    for tempFile in pastFiles:
        if os.path.exists(tempFile):
            print("deleting old csv")
            os.remove(tempFile)


