import pandas as pd

def createDF(rowHeader,index=False):
    """rowHeader is a 1-dimensional tuple of length n where each position contains an embedded tuple of dimension
       1x2 containing the column string description and column value type (i.e. int,str,float,etc...)"""
    
    dSeries = {}
    headers = []
    for row in rowHeader:
        dSeries[row[0]] = []
        headers.append(row[0])
        
    dfCreated = pd.DataFrame(dSeries,columns=headers)
    return dfCreated
        
        
ek2RowTypes = {"pcb":(('Board',str),('Software version',float),('Software checksum',str),('Serial number',int)),
            "measure":(('Board',str),('SEN',str),('Ref(pk-pkV)',int),('ChA(pk-pkV)',int),('ChB(pk-pkV)',int),('ChA(ppm)',int),('ChB(ppm)',int),('temperature',float),('Bulb(V)',int)),
            "lamp":(('Board',str),('LMP',str),('LampSetting',str)),
            "calibration A":(('Board',str),('Channel',str),('Concentration range 1',int),('Concentration range 2',int),('Concentration range 3',int),
                             ('A coefficient 1(bbbc x 10^-c)',int),('A coefficient 2(bbbc x 10^-c)',int),('A coefficient 3(bbbc x 10^-c)',int),
                             ('N coefficient 1(bbbc x 10^-c)',int),('N coefficient 2(bbbc x 10^-c)',int),('N coefficient 3(bbbc x 10^-c)',int),
                             ('Alphapos',int),('Alphaneg',int),
                             ('Betapos 1',int),('Betapos 2',int),('Betapos 3',int),
                             ('Betaneg 1',int),('Betaneg 2',int),('Betaneg 3',int),
                             ('Zero',int),('Span',int),('Span Gas Concentration',int),
                             ('Delay Time (ms)',int),('Current Range',str),
                             ('Temp Sensor Type',int),('Duel or Signle sensor',str),('Temperature (C)',float)),
            "calibration B":(('Board',str),('Channel',str),('Concentration range 1',int),('Concentration range 2',int),('Concentration range 3',int),
                             ('A coefficient 1(bbbc x 10^-c)',int),('A coefficient 2(bbbc x 10^-c)',int),('A coefficient 3(bbbc x 10^-c)',int),
                             ('N coefficient 1(bbbc x 10^-c)',int),('N coefficient 2(bbbc x 10^-c)',int),('N coefficient 3(bbbc x 10^-c)',int),
                             ('Alphapos',int),('Alphaneg',int),
                             ('Betapos 1',int),('Betapos 2',int),('Betapos 3',int),
                             ('Betaneg 1',int),('Betaneg 2',int),('Betaneg 3',int),
                             ('Zero',int),('Span',int),('Span Gas Concentration',int),
                             ('Delay Time (ms)',int),('Current Range',str),
                             ('Temp Sensor Type',int),('Duel or Signle sensor',str),('Temperature (C)',float)),
            "zero A":(('Board',str),('Channel',str),('Parameter',str),('Zero (Act/Ref)',float)),
            "zero B":(('Board',str),('Channel',str),('Parameter',str),('Zero (Act/Ref)',float)),
            "span A":(('Board',str),('Channel',str),('Parameter',str),('Span (Act/Ref*Zero)',float)),
            "span B":(('Board',str),('Channel',str),('Parameter',str),('Span (Act/Ref*Zero)',float))
            }

ek3RowTypes = {"pcb":(('Board',str),('Software version',float),('Software checksum',str),('Serial number',int)),
               "measure":(('Board',str),('SEN',str),('Bias(mV)',int),('Concentration(ppm*100)',str),('OutputCurrent(nA)',str),('EC_SpanConcentration(ppm*100)',str),('SpanCurrent(nA)',str),('temperature',float),('Current Range',str),('Selected Range',str)),         
                }

if __name__ == "__main__":
    dfTest = createDF(rowTypes["calibration A"])
    print(dfTest)
