import re
import os
import psycopg2

def ParseTime(TimeString):
    TimeStringArray = TimeString.split()
    DateArray = TimeStringArray[0].split('-')
    
    return DateArray[1] + '/' + DateArray[2] + '/' + DateArray[0] + ' ' + TimeStringArray[1]

def GenerateConcatFile(FileType):
    Files = os.listdir('.')
    
    Exists = 0
    for File in Files:
        if FileType in File:
            Exists = 1
            
    if Exists == 0:
        return
        
    output = open(FileType, 'w')
    
    FileCount = 0
    for File in Files:
        if FileType in File:
            print File
            
            input = open(File)
            
            FileLine = 0
            while 1:
                Line = input.readline()
                if not Line:
                    break
                    
                if FileCount == 0 and FileLine == 0:
                    output.write(Line)
                    
                elif FileLine > 0:
                    output.write(Line)
                
                FileLine += 1
                
            input.close()
            FileCount += 1
        
    output.close()

def RemoveUnwanted():
    Files = ['Temperature.csv', 'TemperatureParsed.csv', 'TemperatureAvg.csv',
                'GasFlow.csv', 'GasFlowParsed.csv',
                'API200A.csv', 'API200AParsed.csv',
                'DustTrak.csv', 'DustTrakParsed.csv',
                'MetOne.csv', 'MetOneParsed.csv',
                'Teclog.txt', 'TeclogParsed.csv'
            ]
    
    for File in Files:
        if os.path.isfile(File):
            print "Removing {}".format(File)
            os.unlink(File)
            

def ParseTemp():
    if not os.path.isfile('Temperature.csv'):
        return

    input = open('Temperature.csv')
    output = open('TemperatureParsed.csv', 'w')
    OutputAvg = open('TemperatureAvg.csv', 'w')
    OutputAvg.write("TempAvgTime,TempAvgTimeAmbient,TempAvgTimeHood,TempAvgTimeDeltaT,TempAvgTimeSlope,TempAvgTimeHoodState\n")

    while 1:
        Line = input.readline()
        Line = Line.strip()
        
        if not Line:
            break
        
        LineArray = Line.split(',')
        p = re.compile('\d')
        m = p.search(LineArray[0])
        if m:
            LineArray[0] = ParseTime(LineArray[0])
        
        if len(LineArray) == 4:
            output.write(','.join(LineArray) + "\n");
        else:
            OutputAvg.write(','.join(LineArray) + "\n")

def ParseGas(InputName):
    if not os.path.isfile(InputName):
        return
 
    input = open(InputName)
    
    TempArray = InputName.split('.')
    OutputName = TempArray[0] + 'Parsed.csv'
    output = open(OutputName, 'w')
    output.write("GasTime,GasFlow\n")

    while 1:
        Line = input.readline()
        Line = Line.strip()
        
        if not Line:
            break
        
        LineArray = Line.split(',')
        p = re.compile('\d')
        m = p.search(LineArray[0])
        if m:
            LineArray[0] = ParseTime(LineArray[0])
        
        output.write(LineArray[0] + ',' + LineArray[5] + "\n");

def ParseTeclog(InputName):
    if not os.path.isfile(InputName):
        return
    
    input = open(InputName)

    conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
    cur = conn.cursor()
    Insert = "insert into teclog (teclogtime, bd,db,egm,oa) values (%s,%s,%s,%s,%s)"
    
    
    while 1:
        Line = input.readline()
        Line = Line.strip()
        
        if not Line:
            break
        
        LA = Line.split(',')
        if "month" in Line:
            continue
        else:
            Timestamp = LA[0] + '/' + LA[1] + '/' + str(2000 + int(LA[2])) + ' ' + LA[3] + ':' + LA[4] + ':'
            Second = int(round(float(LA[5])))
            
            if Second < 10:
                Timestamp += '0' + str(Second)
            else:
                Timestamp += str(Second)
            
            if float(LA[6]) < 0 or float(LA[8]) < 0:
                continue
            else:
                cur.execute(Insert, (Timestamp,190.1 * pow(float(LA[6]), 0.4876), 40.5 * pow(float(LA[8]), 0.5038), LA[12], LA[7]))
    conn.commit()
    cur.close()
    
def ParseOthers(InputName):
    if not os.path.isfile(InputName):
        return
        
    input = open(InputName)
    
    TempArray = InputName.split('.')
    OutputName = TempArray[0] + 'Parsed.csv'
    output = open(OutputName, 'w')
    
    while 1:
        Line = input.readline()
        Line = Line.strip()
        
        if not Line:
            break
        
        LineArray = Line.split(',')
        p = re.compile('\d')
        m = p.search(LineArray[0])
        if m:
            LineArray[0] = ParseTime(LineArray[0])
        
        output.write(','.join(LineArray) + "\n");


ParseTeclog("Teclog.txt")        
"""        
RemoveUnwanted()
Files = ['Temperature.csv',
            'GasFlow.csv',
            'API200A.csv',
            'DustTrak.csv',
            'MetOne.csv',
            'Teclog.txt',
        ]

for File in Files:
    GenerateConcatFile(File)
    
    if File == 'Temperature.csv':
        ParseTemp()
    elif File == 'GasFlow.csv':
        ParseGas(File)
    elif File == 'Teclog.txt':
        ParseTeclog(File)
    else:
        ParseOthers(File)
"""