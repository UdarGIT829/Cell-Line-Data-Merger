separator = ","

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