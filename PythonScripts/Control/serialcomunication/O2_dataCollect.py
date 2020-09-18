'''
Created on 12/03/2020

@author: Fletcher Gilbertson
'''
def O2_dataCollect():
    from csv_appending import append_list_as_row
    import serial
    import time
    import datetime
    import statistics
    from statistics import mean
    from PythonScripts.Analysis.ConfigurationFiles import configO2
    from PythonScripts.Analysis.ConfigurationFiles.configO2 import dfO2
    import pandas as pd
    import re
    
    #define port names 
    Viciport = '/dev/ttyUSB2'
    IRport = '/dev/ttyUSB1'
    ECport = '/dev/ttyUSB0'
    
    #define machine states
    valve_state = False
    IR_stat = False
    EC_stat = False
    
    t_start = time.time()
    
    def toRow(reading):
        # code used to parase the raw sensor output, isolating parameter strings without having to index string characters directly!!!!!!
        # \\S+ means all non white space characters. This includes words and punctuation. Note: re module can analyze byte strings b''. 
        # re.findall will find all the non-white space characters in the string and dump each found character group into a list element = row
        # .strip() just removes leading and tailing white spaces and carriage returns, in the case of gas sensors it removes leading \r and tailing = \n
        delimiterPattern = "\\S+"
        row = re.findall(delimiterPattern,reading.strip()) 
        row = [x.strip() for x in row]
        return row
    def readlineR(ser,delim):
        timeout = 10
        line = ""
        start = time.time()
        waiting = True
        while(waiting):
            if ser.in_waiting: 
                c = str(ser.read(1),'utf-8')
                line = line + c
                waiting = not line.endswith(delim)
                start = time.time()
            else:
                time.sleep(1.0/ser.baudrate)
                waiting = time.time()-start < timeout
                if not waiting: line = None
        return line.strip()
        
    def comand(ser,comand,length):
        com = False
        while not com:
            ser.read(ser.in_waiting)
            ser.write(comand)
            time.sleep(1)
            line = readlineR(ser,'\r')
            if len(line) == length:
                com = True
                return line 
            else:
                continue
    
    while not valve_state:
        try:
            ser = serial.Serial(Viciport,9600,timeout=0)
            if ser.is_open:
                valve_state = True  
        except:
            time.sleep(1) #delay for 1 second and wait for port to be open
    
    Val_Pos = comand(ser,b'CP\r',16)
    ValNum = int(Val_Pos[15])  
    #Valve position and reactor stream table 
    ReacTable = [0,'R1Outlet','R2Outlet','R3Outlet','R4Outlet','R1Inlet','R2Inlet','R3Inlet','R4Inlet']
    Date = datetime.date.today()
    Time = datetime.datetime.now().time()
    if ser.is_open:
        ser.close()
        valve_state = False
    print('valve ' + Val_Pos)
    
    ser = serial.Serial()   # define function
    ser.baudrate = 9600
    ser.port = ECport
    bytesize=8
    parity='N'
    stopbits=1
    timeout = 0
    xonxoff=0
    rtscts=0
    if not ser.is_open:
        ser.open()
    time.sleep(1)
    print('connected to port' + ECport)
    
    # clear input buffer to sensor 
    while ser.in_waiting > 0:
        ser.read(ser.in_waiting)
    
    # calibration parameters O2 sensor
    slope = -15088 #units nA/(%v/v)
    yinter = 1808 #units nA
    R2 = 99.74
    
    start_measure = time.time()
    cacheCurr = []
    cacheTemp = []
    init = 11 # inital number of iterations to get 10 sensor readings
    while len(cacheCurr) < 10:
        for i in range(init):
            cmd = ser.write(b'[EK3 ECM ENQ]')
            raw = ser.readline() #raw = ser.read(ser.in_waiting) 
            out = str(raw,'utf-8')
            if len(out) != 71:
                continue
#            conc = out[16:24]
#            curr = out[26:35]
#            temp = out[56:61]
            reading = toRow(out)
            conc = reading[3]
            temp = reading[7]
            if out.find('NAK') > 0:
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                break
            #dec = -1*int(curr,16)
            dec = int(conc,16)
            floatTemp = float(temp)
            cacheCurr.append(dec)
            cacheTemp.append(floatTemp)
            time.sleep(1)
            #print(raw)
    ConcDec = mean(cacheCurr)
    TempAve = round(mean(cacheTemp),2)
    end_measure = time.time()
    measure_time = end_measure - start_measure
    print('Sensor measurement time: ' + str(measure_time) +' sec')
    #print(CurrDec, TempAve)
    
    # convert 10 second averaged output current to %v/v
    #O2vv = round((CurrDec-yinter)/slope,5)
    O2vv = round(ConcDec/1000000,4)
    #print(O2vv,TempAve)
    cache = [ReacTable[ValNum],Date,Time,O2vv]     
    myFile = '/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data'+ReacTable[ValNum]+'.csv'
    myRawData = '/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/O2Data.csv'
    append_list_as_row(myFile,cache)
    append_list_as_row(myRawData,cache)
    configO2.cacheO2.append(cache)
    configO2.dfO2 = configO2.dfO2.append(pd.Series(cache,index=dfO2.columns),ignore_index=True)
    
    t_finish =  time.time()
    runtime = t_finish - t_start
    print('Total code runtime: ' +str(runtime)+' sec\n')
