from csv_appending import append_list_as_row
from numpy import std
from statistics import stdev
from viciValve import ViciValve

class Master_control:
    
    def __init__(self,valve,valvTime):
        self.valve = valve
        self.recStream = ''
        self.valvTime = valvTime
        self.ECport = '/dev/ttyUSB0'
        self.Viciport = '/dev/ttyUSB2'
        self.IRport = '/dev/ttyUSB1'
    
    def toRow(self,reading):
        # code used to parase the raw sensor output, isolating parameter strings without having to index string characters directly!!!!!!
        # \\S+ means all non white space characters. This includes words and punctuation. Note: re module can analyze byte strings b''. 
        # re.findall will find all the non-white space characters in the string and dump each found character group into a list element = row
        # .strip() just removes leading and tailing white spaces and carriage returns, in the case of gas sensors it removes leading \r and tailing = \n
        delimiterPattern = "\\S+"
        row = re.findall(delimiterPattern,reading.strip()) 
        row = [x.strip() for x in row]
        return row
    def readlineR(self,ser,delim):
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
        
    def comand(self,ser,comand,length):
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

    def valve_control(self):
        import serial
        import time
        import datetime
        
        #always check to see if vici valve is open or not and wait until free to open
        while True:
            try:
                ser = serial.Serial(self.Viciport,9600,timeout=0)   
                time.sleep(0.1)
            except:
                time.sleep(1) #delay for 1 second and wait for port to be open
                continue
            print('connected to: ' + ser.name)
            break
        
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
        
        # begin valve switching software for measuring gas compositions for all reactors 
        #for i in range(0,len(self.valve)):
#        uni = str(self.valve) # int to string 
#        vint = bytes(uni,'utf-8') # convert string to bytes by encoding with utf-8 to avoid the byte array format
#        ser.write(b'GO0' + vint + b'\r') # ascii string to open vivi valve
#        time.sleep(5)
#        ser.read(ser.in_waiting)
#        ser.write(b'CP\r\n')
#        time.sleep(0.1) 
#        read_val = ser.readline()
#        while read_val != b'Position is  = ' + vint + b'\r':
#            ser.read(ser.in_waiting)
#            ser.write(b'GO0' + vint + b'\r')
#            time.sleep(5)
#            ser.write(b'CP\r\n')
#            time.sleep(0.1) 
#            read_val = ser.read(ser.in_waiting)
        
        #Valve move comands
        v = ViciValve()
        v.connect()
        v.setup() #Really only need to check this once a day
        v.move(self.valve)
        valve_position = v.interpretPosition()
        stop()
        print(valve_position)
        self.recStream = valve_position
        now = datetime.datetime.now(tz=None)    # date and time stap for valve position
        print(now) # print date and time stap after confirming valve has switched to the desired position 
    
    # determine if it's a inlet or outlet stream and print reactor selected 
#        if self.valve < 5:
#            flow1 = 'Outlet'
#            print('R' + uni + ' ' + flow1 + '\n')
#            self.recStream = 'R' + uni + flow1      
#        else:
#            flow2 = 'Inlet'
#            itr = str(self.valve-4)
#            print('R' + itr + ' ' + flow2 + '\n')
#            self.recStream = 'R' + itr + flow2
##                 myFile = 'C:\Program Files (x86)\Eclipse\Reactor Control\particlecamp-master\PythonScripts\DAQ\Collected\GasData.csv'
##                 append_list_as_row(myFile,cache)
#
#        ser.close()
    
    def IR_dataCollect(self):
        import time
        from IRClean import cleanIR
        from find_comPort import serial_ports
        from serial.tools import list_ports_common
        from numpy.core.defchararray import rstrip
        import csv 
        from numpy import exp
        import math
        import statistics as st
        from statistics import mean
        import serial
        import datetime
        import io
        import pandas as pd
        import numpy as np
        
        start_time = time.time()
        ser = serial.Serial()   # define function
        ser.baudrate = 9600
        ser.port = self.IRport
        bytesize=8
        parity='N'
        stopbits=1
        timeout = 0
        xonxoff=0
        rtscts=0
        if ser.is_open == False:
            ser.open()
        time.sleep(1)
        
        # clearing IR sensor buffer and switching to 'set-up' mode
        bytestoread = ser.in_waiting
        str(ser.read(bytestoread),'utf-8')
        while bytestoread > 0:
            bytestoread = ser.in_waiting
            ser.close() #always close port before calling clean()
            cleanIR(ser.port)
            if ser.is_open == False:
                ser.open()
            time.sleep(1)
            if ser.in_waiting > 0:
                continue
        print(ser.port + ' is clear.')
        
        # getting sensor serial number and firmware version
        ser.read(ser.in_waiting)
        ser.write(b'[WHO]')
        res = rstrip(str(ser.readline()))
        print(res)
        
        # asks the sensors for the calibration data and Zero and Span information
        ser.read(ser.in_waiting)
        # creating data frame to store calibration parameters
        
        chp = ['A','B']
        for i in range(2):
            ch = bytes(chp[i],'utf-8')
            setup = ser.write(b'[EK2 CA' + ch + b' ENQ]')
            time.sleep(0.1)
            a_c = ser.readline()
            chksum = str(a_c,'utf-8')
            while chksum.find('[EK2 CA'+chp[i]) == -1:
                ser.read(ser.in_waiting)
                setup
                a_c = ser.readline()
                chksum = str(a_c,'utf-8')
                time.sleep(0.1)
            if i == 0:
                CH4_coffA = round(float(a_c[38:42])*0.0001,6)#A coefficient position in string output from sensor
                CH4_coffN = round(float(a_c[53:58])*0.0001,6)#N coefficient position in string output from sensor  
                AlphaposCH4 = 0.0004 #eventually go back and have code find string characters which correspond to to parameters
                AlphanegCH4 = 0.0004
                BetaposCH4 = -0.059
                BetanegCH4 = -0.059
            elif i ==1:
                CO2_coffA = round(float(a_c[44:49])*0.0001,6)
                CO2_coffN = round(float(a_c[59:62])*0.001,6) 
                AlphaposCO2 = 0.0005
                AlphanegCO2 = 0.0005
                BetaposCO2 = 0.4
                BetanegCO2 = 0.4
            ser.read(ser.in_waiting)
            ser.write(b'[EK2 CA' + ch + b' ZERO ENQ]')
            r2 = ser.readline()
            x = str(r2,'utf-8')
            if i ==0:
                clc = x[15:23]
                ZeroCH4 = round(float(clc),5)
            elif i ==1:
                clc = x[15:23]
                ZeroCO2 = round(float(clc),5)
        
            ser.read(ser.in_waiting)
            ser.write(b'[EK2 CA' + ch + b' SPAN ENQ]')
            r3 = ser.readline()
            x = str(r3,'utf-8')
            if i ==0:
                clc = x[15:23]
                SpanCH4 = round(float(clc),6)
            elif i==1:
                clc = x[15:23]
                SpanCO2 = round(float(clc),6)
        #print(AlphaposCH4,AlphanegCH4,BetaposCH4,BetanegCH4)
        
        # data frame containing calibration coefficients stored in sensor memory 
        d = {
            'Channel A-CH4':[ZeroCH4,SpanCH4,CH4_coffA,CH4_coffN,AlphaposCH4,AlphanegCH4,BetaposCH4,BetanegCH4],
            'Channel B-CO2':[ZeroCO2,SpanCO2,CO2_coffA,CO2_coffN,AlphaposCO2,AlphanegCO2,BetaposCO2,BetanegCO2],
            'Parameter':['Zero','Span','A coefficient','N coefficient','Alphapos','Alphaneg','Betapos','Betaneg']}
        df = pd.DataFrame(d,columns=['Parameter','Channel A-CH4','Channel B-CO2'])
        #print(df)
        # indexing use this command: df.iloc[x,y] x=row and y=column
    
        # import calibration data 
        dataC = pd.read_csv(r'/home/pi/BTF_reactors/PythonScripts/Analysis/DataSummary/GasCalibrationData/MATLAB_Calibration_data_IR_sensor.csv')
        dfC = pd.DataFrame(dataC, columns=['CH4 Gas Standard (%v/v)','CH4 NormAbs Ave','CH4 NormAbs STD','Reference Volt 1','CO2 Gas Standard (%v/v)','CO2 NormAbs Ave','CO2 NormAbs STD','Reference Volt 2'])
        
        # Avrami fitting parameters from MATLAB fitting (eventually should create module in python to curve fit similar to matlab script or call .m script 
        # These coefficients i entered to the SGX sensor software, however, I don't call this data frame data when calcuating the gas concentration below. 
        # Inestead I call the local variables called from the sensors non-volatile memory above.
        # In the future I should have the code below above the code for calling the coefficients from the sensor memory. Also I should develop a python code for analyzing calibration gases like I've done in matlab
        d0 = {'Gas':['CH4','CO2'],
             'A Coefficient':[0.0417,0.3824],
             'N Coefficient':[0.6143,0.4523]}
        dfCoff = pd.DataFrame(d0,columns=['Gas','A Coefficient','N Coefficient'])
        
        #data frame to store 10 sec average values
        dGas = {'Reactor Stream':[],
                'Date':[],
                'Time':[],
                'CH4 (%v/v)':[],
                'CO2 (%v/v)':[],
                'Temperature (C)':[]}
        dfGas = pd.DataFrame(dGas,columns=['Reactor Stream','Date','Time','CH4 (%v/v)','CO2 (%v/v)','Temperature (C)'])
    
        ser.read(ser.in_waiting)
        # clearing IR sensor buffer and switching to 'measurement' mode
        while ser.in_waiting == 0:
            ser.read(ser.in_waiting)
            ser.write(b'[EK2 SEN MEA]')
            ser.readline()
            time.sleep(0.1)
        ser.readline()
        #local data storage
        LocStorCH4 = []
        LocStorCO2 = []
        LocStorTemp = []
        CH4data = []
        CO2data = []
        Tempdata = []
    #     DAC_Vrange = 3
    #     Hex_range = 65535 #FFFF is the maximum possible hexdecimal output from the amplified voltage from the sensor output
    #     T_calb = 25 #average temperature of gas during calibration
        for i in range(0,self.valvTime):
            x = str(ser.readline(),'utf-8')
            while x.find('NAK') > 0:
                x = str(ser.readline(),'utf-8')
                continue
                while x.find('ACK') > 0:
                    x = str(ser.readline(),'utf-8')
                    continue
                continue
            CH4 = round((int(x[26:32])/1E6)*100,4)
            CO2 = round((int(x[34:40])/1E6)*100,4)
            Temp = float(x[42:46])
            ## This section outlines how to manually grab hexadecimal outputs from the hardware and convert these values to decimal and compensate for tempeature ##
            ## NOTE: this method is very involved, especially if your gas stream temperature swings > +/- 5C 
    #         BulbV = int(x[47:51],16)*DAC_Vrange/Hex_range
    #         Ref = int(x[10:14],16)*DAC_Vrange/Hex_range
    #         ChA = int(x[15:19],16)*DAC_Vrange/Hex_range
    #         ChB = int(x[20:24],16)*DAC_Vrange/Hex_range
    #         NA_CH4 = 1 - (ChA/Ref/ZeroCH4) 
    #         NA_CO2 = 1 - (ChB/Ref/ZeroCO2)
    #         # Alpha temperature compensation 
    #         NT_CH4 = 1 - NA_CH4
    #         NT_CO2 = 1 - NA_CO2
    #         #print(NT_CH4,NT_CO2)
    #         if Temp >= T_calb:
    #             NT_CH4comp = NT_CH4*(1+(AlphaposCH4*(Temp-T_calb)))
    #             Span_CH4comp = SpanCH4+(BetaposCH4*(Temp-T_calb)/T_calb)
    #             NT_CO2comp = NT_CH4*(1+(AlphaposCO2*(Temp-T_calb)))
    #             Span_CO2comp = SpanCO2+(BetaposCO2*(Temp-T_calb)/T_calb)
    #             #print(NT_CH4comp,Span_CH4comp,NT_CO2comp,Span_CO2comp)
    #         elif Temp < T_calb:
    #             NT_CH4comp = NT_CH4*(1+(AlphanegCH4*(T_calb-Temp)))
    #             Span_CH4comp = SpanCH4+(BetanegCH4*(T_calb-Temp)/T_calb)
    #             NT_CO2comp = NT_CO2*(1+(AlphanegCO2*(T_calb-Temp)))
    #             Span_CO2comp = SpanCO2+(BetanegCO2*(T_calb-Temp)/T_calb)
                #print(NT_CH4comp,Span_CH4comp,NT_CO2comp,Span_CO2comp)
    #         CH4 = math.pow(-np.log(1-((1-NT_CH4comp)/Span_CH4comp))/CH4_coffA,1/CH4_coffN)
    #         CO2 = math.pow(-np.log(1-((1-NT_CO2comp)/Span_CO2comp))/CO2_coffA,1/CO2_coffN)
            # store per second data in array which acts as short term local data storage in between iterations
            LocStorCH4.append(CH4)
            LocStorCO2.append(CO2)
            LocStorTemp.append(Temp)
            if i%10 == 0: # averaging every 10 seconds and time stamp 
                avgCH4 = round(mean(LocStorCH4),4)
                avgCO2 = round(mean(LocStorCO2),4)
                avgTemp = (mean(LocStorTemp))
                Time = datetime.datetime.now().time()
                Date = datetime.date.today()
                #for now we will assume after 30min the readings are stable and just take average in this region (30-60min) I need to develop code similar to matlab code for looking at whether data is stable or I need to filter out spikes like Pete suggested
                if i >= self.valvTime/2:
                    CH4data.append(avgCH4)
                    CO2data.append(avgCO2)
                    Tempdata.append(avgTemp)
                LocStorCH4.clear()
                LocStorCO2.clear()
                LocStorTemp.clear()
                cache = [self.recStream,Date,Time,avgCH4,avgCO2,avgTemp]
                dfGas = dfGas.append(pd.Series(cache,index=dfGas.columns),ignore_index=True)
                
                myFile = '/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasData.csv'
                append_list_as_row(myFile,cache)
                cache.clear()
            if i == self.valvTime - 1: #need -1 because iteration always starts at index=0
                CH4Fin = round(mean(CH4data[int(len(CH4data)/2):int(len(CH4data))]),4) # takes average of last half of 3700 data points, first half sensor reading ins't stable/still purging
                CH4std = round(stdev(CH4data[int(len(CH4data)/2):int(len(CH4data))]),4)
                CO2Fin = round(mean(CO2data[int(len(CO2data)/2):int(len(CO2data))]),4)
                CO2std = round(stdev(CO2data[int(len(CO2data)/2):int(len(CO2data))]),4)
                TempFin = round(mean(Tempdata),4)
                Time2 = datetime.datetime.now().time()
                Date2 = datetime.date.today()
                Finale = [self.recStream,Date2,Time2,CH4Fin,CH4std,CO2Fin,CO2std,TempFin]
                myFile2 = '/home/pi/BTF_reactors/PythonScripts/DAQ/Collected/GasDataFinal_'+self.recStream+'.csv'
                append_list_as_row(myFile2,Finale)
                print(Finale)
        CH4data.clear()
        CO2data.clear()
        #print(dfGas)
        
        #clear serial buffer by reading and then switch to 'set-up' mode and close port
        bytestoread = ser.in_waiting
        str(ser.read(bytestoread),'utf-8')
        while bytestoread > 0:
            bytestoread = ser.in_waiting
            ser.close() #always close port before calling clean()
            cleanIR(ser.port)
            if ser.is_open == False:
                ser.open()
            time.sleep(0.1)
            if ser.in_waiting > 0:
                continue
        print(ser.port + ' is clear.')
        if ser.is_open == True:
            ser.close()
            print(ser.port + ' closed.')
        
        runTimeIR = round(time.time() - start_time,1)
        print(runTimeIR) #seconds to run python module for taking gas samples

    
