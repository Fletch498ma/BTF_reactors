import time
import psycopg2
from datetime import datetime 

conn = psycopg2.connect("host='mmlunden-s67.dhcp.lbl.gov' port='5432' dbname='mydb' user='melissa' password='postgres'")
cur = conn.cursor()

StartTime = '4/9/2010 19:00'
EndTime = '4/9/2015 20:00'

OutputFiles = [
        'API.csv',
        'DustTrak.csv',
        'Gas.csv',
        'MetOne.csv',
        'Teclog.csv'
    ]
    
APIHeaders = [
        'APITime',
        'NO',
        'NO2',
        'NOx'
    ]
    
DustTrakHeaders = [
        'DustTrakTime',
        'DustTrakConc'
    ]
    
GasHeaders = [
        'GasTime',
        'GasFlow'
    ]
    
MetOneHeaders = [
        'MetOneTime',
        'MetOne03',
        'MetOne05',
        'MetOne07',
        'MetOne1',
        'MetOne2',
        'MetOne5'
    ]
    
TeclogHeaders = [
        'TeclogTime',
        'BD',
        'DB',
        'EGM'
    ]
    
def WriteHeaders(Output, Headers):
    Output.write(','.join(Headers))
    Output.write("\n")
   
def WriteData(Output, Select):
    cur.execute(Select)
    rows = cur.fetchall()
    
    for row in rows:
        Count = 0
        RowLength = len(row)
        for val in row:
            if Count < RowLength - 1:
                Output.write("{},".format(val))
            else:
                Output.write( "{}\n".format(val))
            
            Count += 1
for OutputFile in OutputFiles:
    Output = open(OutputFile, 'w')
    
    if 'API' in OutputFile:
        WriteHeaders(Output, APIHeaders)
        WriteData(Output, "select to_char(apitime, 'MM/DD/YYYY HH24:MI:SS'),no,no2,nox from api where apitime >= '{}' and apitime <= '{}' order by apitime".format(StartTime, EndTime))
    elif 'DustTrak' in OutputFile:
        WriteHeaders(Output, DustTrakHeaders)
        WriteData(Output, "select to_char(dusttraktime, 'MM/DD/YYYY HH24:MI:SS'),dtconc from dusttrak where dusttraktime >= '{}' and dusttraktime <= '{}' order by dusttraktime".format(StartTime,EndTime))
    elif 'Gas' in OutputFile:
        WriteHeaders(Output, GasHeaders)
        WriteData(Output, "select to_char(gastime, 'MM/DD/YYYY HH24:MI:SS'),gasflow from gas where gastime >= '{}' and gastime <= '{}' order by gastime".format(StartTime,EndTime))
    elif 'MetOne' in OutputFile:
        WriteHeaders(Output, MetOneHeaders)
        WriteData(Output, "select to_char(metonetime, 'MM/DD/YYYY HH24:MI:SS'),metone03,metone05,metone07,metone1,metone2,metone5 from metone where metonetime >= '{}' and metonetime <= '{}' order by metonetime".format(StartTime,EndTime))
    elif 'Teclog' in OutputFile:
        WriteHeaders(Output, TeclogHeaders)
        WriteData(Output, "select to_char(teclogtime, 'MM/DD/YYYY HH24:MI:SS'),bd,db,egm from teclog where teclogtime >= '{}' and teclogtime <= '{}' order by teclogtime".format(StartTime,EndTime))

    Output.close()
conn.close()