# Neph output string: 4.460e-06  5.828e-04 1003 296 99 00
# Column idenity: bscat (m-1), calibrator coef (,-1), pressure (mb), temp (K), RH (%), relay status
while 1:
    Line = ser.readline()
    LineArray = Line.split()
    values = (float(LineArray[0]),float(LineArray[1]))
    toAvg.append(values)
    if len(LineArray)<5:
        print "Error an invalid number of lines was sent."
    elif math.floor(time.time())%60 == 0:
        avgVal = (sum(zip(*toAvg)[0])/len(toAvg),sum(zip(*toAvg)[1])/len(toAvg))
        timeStr = time.strftime("%Y-%m-%d %H:%M:%S") 
        toFile = ", ".join([INSTR,timeStr]+LineArray)
        display = ", ".join([INSTR,timeStr]+list(map(str,values)))
        toAvg=[]
        time.sleep(1)
