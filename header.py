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
    def __init__(self,drug_treatments = None):
        if drug_treatments == None:
            drug_treatments = list()
        self.drug_treatments = drug_treatments # list of drug_treatment objects
    def getData(self):
        return self.drug_treatments
    def addToTreatments(self, newDrugTreatment):
        self.drug_treatments.append(newDrugTreatment)

class job:
    def __init__(self,name = None,date = None,control = None, treatments = None):
        if control != None:
            self.control = control
        if treatments != None:
            self.treatments = treatments
        else:
            self.treatments = list()
        self.Name = name
        self.Date = date
    def __str__(self):
        toString = list()
        toString.extend( (self.Name,self.Date, self.control.cellLines) )
        return str(toString)
    def asOutput(self):
        output = list()

        for tPlates in self.treatments:
            for tPlate in tPlates:
                for dTreatment in tPlate.drug_treatments:
                    for cLine in dTreatment.cellLines:
                        row = list()
                        Control_position = cLine[0]
                        Treatmentposition = cLine[1]
                        cl_name = cLine[2]
                        row.extend( (dTreatment.barcode, Treatmentposition, self.Name, cl_name, self.Date,
                        dTreatment.drugID, " ? ", " ? ", self.control.day1BC, Control_position,
                        self.control.day7BC, Control_position) )
                        output.append(row)
        print(output)
        return output

    def setName(self, newName):
        self.Name = newName
    def setDate(self, newDate):
        self.Date = newDate
    def setControl(self, control):
        self.control = control
    def setTreatments(self, treatments):
        self.treatments.append(treatments)

