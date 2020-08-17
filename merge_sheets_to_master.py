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

from pathlib import Path
def merge_to_csv():
    directory = os.path.dirname(__file__)

    temporaryCsvFileName = "tempMaster.csv"

    excelFiles = list()
    for path in Path(directory).rglob('*.xlsx'):
        print(os.path.abspath(path))
        excelFiles.append(path)

    for excelFile in excelFiles:
        if "master.xlsx" in str(excelFile):
            excelFiles.remove(excelFile)
        if "master.csv" in str(excelFile):
            excelFile.remove(excelFile)

    if os.path.exists(temporaryCsvFileName):
        print("deleting old Master csv")
        #os.remove(temporaryCsvFileName)

    oldName = ""
    newName = ""
    nameBeenPrinted = False
    print(excelFiles)
    for path in excelFiles:
        print( "Reading file: ", os.path.basename(path) )
        with xlrd.open_workbook(path) as workbook:
            names = workbook.sheet_names()
            sheetAmount = len(names)
            for index in range(sheetAmount):
                print("Reading sheet #: ", index+1)
                sheet = workbook.sheet_by_index(index)
                tempSheetName = "sheet" + str(index+1) + ".csv"
                with open(temporaryCsvFileName, 'a+', newline="") as file:
                    col = csv.writer(file)
                    for row in range(sheet.nrows):
                        if 'Name: ' in str(sheet.row_values(row)):
                            if not nameBeenPrinted:
                                oldName = sheet.row_values(row)
                                col.writerow(sheet.row_values(row))
                                nameBeenPrinted = True
                            else:
                                newName = sheet.row_values(row)
                                if oldName != newName:
                                    col.writerow(sheet.row_values(row))    
                        else:
                            col.writerow(sheet.row_values(row))
                    col.writerow('')
                    file.close()
    return(temporaryCsvFileName)

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

    finalCsvFileName = "tempMaster2.csv"
    with open(finalCsvFileName, 'a+', newline="") as file:
        col = csv.writer(file)
        if header:
            col.writerow(headerText)
        for row in input:
            col.writerow(row)
        file.close()
    return finalCsvFileName

def clean_temp_files():
    directory = os.path.dirname(__file__)

    pastFiles = list()

    for path in Path(directory).rglob('tempMaster.csv'):
        pastFiles.append(path)

    for path in Path(directory).rglob('tempMaster2.csv'):
        pastFiles.append(path)

    for tempFile in pastFiles:
        if os.path.exists(tempFile):
            print("deleting old csv")
            os.remove(tempFile)


