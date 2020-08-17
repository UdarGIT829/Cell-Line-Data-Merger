separator = ","
import csv
from merge_sheets_to_master import *

class control_plate:
    def __init__(self,day1bc, day7bc, cellLines):
        self.day1BC = day1bc
        self.day7BC = day7bc
        self.cellLines = cellLines #will be stored as: (cellLine-ID : position) eg=(C1:1 ; C2:2 ; ...)
    def getPlateBC():
        return self.barcode
    def getDay1BC():
        return self.day1BC
    def getDay7BC():
        return self.day7BC
    def getCellLines():
        return cellLines

class drug_treatment:
    def __init__(self,drugName, TR_barcode, cellLines):
        self.barcode = TR_barcode
        self.drugID = drugName
        self.cellLines = cellLines #will be stored as: (Cposition ,Tposition, cellLine-ID) eg=(1-2,C1 ; 3-4, C2 ; ...)

class treatment_plate:
    def __init__(self,drug_treatments):
        self.drug_treatments = drug_treatments # list of drug_treatment objects
    def getData(self):
        return self.drug_treatments
    def addToTreatments(self, newDrugTreatment):
        self.drug_treatments.append(newDrugTreatment)

class job:
    def __init__(self,name,date,control = None, treatments = None):
        if control != None:
            self.control = control
        if treatments != None:
            self.treatments = treatments
        else:
            self.treatments = list()
        self.Name = name
        self.Date = date
    def __str__(self):
        toPrint = list()
        toString = ""
        for trt_plate in self.treatments:
            for dt in trt_plate.drug_treatments:
                for cl in dt.cellLines:
                    Control_position = cl[0]
                    Treatmentposition = cl[1]
                    cl_name = cl[2]
                    toPrint.extend((dt.barcode, separator, Treatmentposition, separator, self.Name, separator, cl_name, separator, self.Date,
                    separator, dt.drugID, separator, "? ", separator, "? ", self.control.day1BC, separator, Control_position, 
                    separator, self.control.day7BC, separator, Control_position ))
        toString = toString + str(toPrint)
        return toString
    def asOutput(self):
        output = list()
        for trt_plate in self.treatments:
            for dt in trt_plate.drug_treatments:
                for cl in dt.cellLines:
                    row = list()
                    Control_position = cl[0]
                    Treatmentposition = cl[1]
                    cl_name = cl[2]
                    row.extend((dt.barcode, Treatmentposition , self.Name , cl_name , self.Date,
                    dt.drugID , "? " , "? ", self.control.day1BC , Control_position, 
                    self.control.day7BC , Control_position ))
                    output.append(row)
        return output
    def setControl(self, control):
        self.control = control
    def setTreatments(self, treatments):
        self.treatments.append(treatments)

def csv_to_data(inputFilename):
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
                    if activeJob != None:
                        print("==========")
                        print("Saved JOB!")
                        print("==========")
                        jobList.append(activeJob)
                        activeJob = None
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

    return jobList

def data_to_xlsx(jobList):
    needHeader = True
    for singularjob in jobList:
        finalcsvName = modified_to_csv( singularjob.asOutput(),needHeader )
        needHeader = False
        print("Exported to: ", finalcsvName)
    csv_to_master(finalcsvName)

