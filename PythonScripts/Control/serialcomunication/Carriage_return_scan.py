def carriage_scan(byte):
    'Converts input data into string and finds carriage return'
    byte = str(byte,'utf-8')
    if byte.find('\n') > 0:
        byte.replace('\n','')
##    if byte.find('\r') > 0:
##        byte.replace('\r','')
    return(byte)

