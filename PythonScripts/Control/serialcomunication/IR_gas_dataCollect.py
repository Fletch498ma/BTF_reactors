def IR_dataCollect():
    from IRClean import clean
    from find_comPort import serial_ports
    from serial.tools import list_ports_common
    from numpy.core.defchararray import rstrip
    import csv 
    from numpy import exp
    import math
    import statistics as st
    from statistics import mean
    import serial
    import time
    import datetime
    import io
    import pandas as pd
    import numpy as np
    
    ser = serial.Serial()   # define function
    ser.baudrate = 9600
    ser.port = 'COM4'
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
        c = clean(ser.port)
        c.cleanIR()
        if ser.is_open == False:
            ser.open()
        time.sleep(1)
        if ser.in_waiting > 0:
            continue
    print(ser.port + ' is clear.')
    
    # getting sensor serial number and firmware version
    ser.reset_input_buffer()
    ser.write(b'[WHO]')
    res = rstrip(str(ser.readline()))
    print(res)
    
    # asks the sensors for the calibration data and Zero and Span information
    ser.read(ser.in_waiting)
    # creating data frame to store calibration parameters
    
    chp = ['A','B']
    for i in range(0,2):
        ch = bytes(chp[i],'utf-8')
        ser.read(ser.in_waiting)
        ser.write(b'[EK2 CA' + ch + b' ENQ]')
        r1 = ser.readline()
        a_c = str(r1,'utf-8')
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
    d = {
        'Channel A-CH4':[ZeroCH4,SpanCH4,CH4_coffA,CH4_coffN,AlphaposCH4,AlphanegCH4,BetaposCH4,BetanegCH4],
        'Channel B-CO2':[ZeroCO2,SpanCO2,CO2_coffA,CO2_coffN,AlphaposCO2,AlphanegCO2,BetaposCO2,BetanegCO2],
        'Parameter':['Zero','Span','A coefficient','N coefficient','Alphapos','Alphaneg','Betapos','Betaneg']}
    df = pd.DataFrame(d,columns=['Parameter','Channel A-CH4','Channel B-CO2'])
    print(df)
    # indexing use this command: df.iloc[x,y] x=row and y=column
    
    # clearing IR sensor buffer and switching to 'measurement' mode
    str(ser.read(ser.in_waiting),'utf-8')
    t0=ser.in_waiting
    time.sleep(1)
    tf=ser.in_waiting
    while tf == t0:
        t0=ser.in_waiting
        time.sleep(1)
        tf=ser.in_waiting
        ser.read(ser.in_waiting)
        ser.write(b'[EK2 SEN MEA]')
        meareturn = str(ser.read(size=ser.in_waiting),'utf-8')
        if meareturn.find('[ACK]') > 0:
            print(meareturn)
            break
        ser.read(size=ser.in_waiting)
    
    # import calibration data 
    dataC = pd.read_csv(r'C:\Program Files (x86)\Eclipse\Reactor Control\BTF_reactors\PythonScripts\Analysis\DataSummary\GasCalibrationData\MATLAB_Calibration data IR sensor.csv')
    dfC = pd.DataFrame(dataC, columns=['CH4 Gas Standard (%v/v)','CH4 NormAbs Ave','CH4 NormAbs STD','Reference Volt 1','CO2 Gas Standard (%v/v)','CO2 NormAbs Ave','CO2 NormAbs STD','Reference Volt 2'])
    
    # Avrami fitting parameters from MATLAB fitting (eventually should create module in python to curve fit similar to matlab script or call .m script 
    d0 = {'Gas':['CH4','CO2'],
         'A Coefficient':[0.0417,0.3824],
         'N Coefficient':[0.6143,0.4523]}
    dfCoff = pd.DataFrame(d0,columns=['Gas','A Coefficient','N Coefficient'])
    print(dfCoff)
    
    T_calb = 25 #average temperature of gas during calibration 
    dfGas = pd.DataFrame()
    timeStamp = []
    storCH4 = []
    storCO2 = []
    storTemp = []
    DAC_Vrange = 3
    Hex_range = 65535 #FFFF is the maximum possible hexdecimal output from the amplified voltage from the sensor output
    end_iter = 10000 #number of iterations to run, i.e. number of sensor points to take during reading
    
    for i in range(0,end_iter):
        if i == 0: 
            ser.readline()
            continue
        x = str(ser.readline(),'utf-8')
        Temp = float(x[42:46])
        BulbV = int(x[47:51],16)*DAC_Vrange/Hex_range
        Ref = int(x[10:14],16)*DAC_Vrange/Hex_range
        ChA = int(x[15:19],16)*DAC_Vrange/Hex_range
        ChB = int(x[20:24],16)*DAC_Vrange/Hex_range
        NA_CH4 = 1 - (ChA/Ref/ZeroCH4) 
        NA_CO2 = 1 - (ChB/Ref/ZeroCO2)
        # Alpha temperature compensation 
        NT_CH4 = 1 - NA_CH4
        NT_CO2 = 1 - NA_CO2
        #print(NT_CH4,NT_CO2)
        if Temp >= T_calb:
            NT_CH4comp = NT_CH4*(1+(AlphaposCH4*(Temp-T_calb)))
            Span_CH4comp = SpanCH4+(BetaposCH4*(Temp-T_calb)/T_calb)
            NT_CO2comp = NT_CH4*(1+(AlphaposCO2*(Temp-T_calb)))
            Span_CO2comp = SpanCO2+(BetaposCO2*(Temp-T_calb)/T_calb)
            #print(NT_CH4comp,Span_CH4comp,NT_CO2comp,Span_CO2comp)
        elif Temp < T_calb:
            NT_CH4comp = NT_CH4*(1+(AlphanegCH4*(T_calb-Temp)))
            Span_CH4comp = SpanCH4+(BetanegCH4*(T_calb-Temp)/T_calb)
            NT_CO2comp = NT_CO2*(1+(AlphanegCO2*(T_calb-Temp)))
            Span_CO2comp = SpanCO2+(BetanegCO2*(T_calb-Temp)/T_calb)
            #print(NT_CH4comp,Span_CH4comp,NT_CO2comp,Span_CO2comp)
        CH4 = math.pow(-np.log(1-((1-NT_CH4comp)/Span_CH4comp))/CH4_coffA,1/CH4_coffN)
        CO2 = math.pow(-np.log(1-((1-NT_CO2comp)/Span_CO2comp))/CO2_coffA,1/CO2_coffN)
        # store per second data in array which acts as short term local data storage in between iterations
        LocStorCH4 = []
        LocStorCO2 = []
        LocStorTemp = []
        LocStor_CH4.append(CH4)
        LocStorCO2.append(CO2)
        LocStorTemp.append(Temp)
        if i%10 < 1: # averaging every 10 seconds and time stamp 
            avgCH4 = round(mean(storCH4),4)
            avgCO2 = round(mean(storCO2),4)
            avgCTemp = mean(storTemp) 
            timeStamp.append(datetime.datetime.now(tz=None))
        #print(CH4,CO2,Temp)
        LocStorCH4.clear()
        LocStorCO2.clear()
        LocStorTemp.clear()
    outThread = [storCH4,storCO2,storTemp]
    print(outThread)
    ser.close()
        
    
    
