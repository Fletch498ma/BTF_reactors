import psycopg2
from datetime import datetime, date
import numpy as np

Experiments = [1,2,3]

#Make database connection
conn = psycopg2.connect("dbname=mydb user=fletcher password=postgres")
cur = conn.cursor()

def GetGasVolume(Experiments):
	"""
	Returns the total gas volume for experiments listed in Experiments.  This uses the trapezoidal rule
	to calculate the area under the gas flow (LPM) vs Time (s) curve.  Time is stored as a timestamp
	in the database but the query will ask for an epoch which is seconds since 1970.
	"""
	GasResults = []
	for Experiment in Experiments:
		Query = "SELECT EXTRACT(EPOCH FROM g.gastime), g.gasflow / 60 FROM gas g WHERE g.gastime >= (SELECT e.starttime FROM experiments e WHERE e.experiment = {}) AND g.gastime < (SELECT e.endtime FROM experiments e WHERE e.experiment = {}) ORDER BY g.gastime".format(Experiment, Experiment)

		cur.execute(Query)
		Rows = cur.fetchall()
		
		GasTime = []
		GasFlow = []
		for Row in Rows:
			GasTime.append(Row[0])
			GasFlow.append(float(Row[1]))
		
		GasResults.append([Experiment, np.trapz(GasFlow, GasTime)])
	
	return GasResults

def GenOut(Experiment):
    #Generate header information for the output file.
    Output = open("Metone" + Experiment + ".csv", 'w')

    Headers = [
            'b' + Experiment + '_Elapsed,',
            'b' + Experiment + '_03,',
            'b' + Experiment + '_05,',
            'b' + Experiment + '_07,',
            'b' + Experiment + '_1,',
            'b' + Experiment + '_2,',
            'b' + Experiment + '_5',
        ]

    for Header in Headers:
        Output.write(Header)
    Output.write("\n")

    GasVolume = GetGasVolume([int(Experiment)])
    
    Query = "SELECT metonetime,metone03,metone05,metone07,metone1,metone2,metone5 FROM metone WHERE metonetime >= (SELECT starttime - interval '5 minutes' FROM experiments WHERE experiment = {}) AND metonetime < (SELECT endtime + interval '5 minutes' FROM experiments WHERE experiment = {}) ORDER BY metonetime".format(Experiment, Experiment)
    cur.execute(Query)
    rows = cur.fetchall()

    count = 0
    Elapsed = 0
    for row in rows:
        if count == 0:
            lasttime = row[0]
            Output.write( "{},{},{},{},{},{},{}\n".format(0,float(row[1])/GasVolume[0][1],float(row[2])/GasVolume[0][1],float(row[3])/GasVolume[0][1],float(row[4])/GasVolume[0][1],float(row[5])/GasVolume[0][1],float(row[6])/GasVolume[0][1]))
            count += 1
        else:
            Diff = row[0] - lasttime
            Elapsed += Diff.total_seconds()
            Output.write("{},{},{},{},{},{},{}\n".format(Elapsed,float(row[1])/GasVolume[0][1],float(row[2])/GasVolume[0][1],float(row[3])/GasVolume[0][1],float(row[4])/GasVolume[0][1],float(row[5])/GasVolume[0][1],float(row[6])/GasVolume[0][1]))
            lasttime = row[0]
    Output.close()

for Experiment in Experiments:
    GenOut(str(Experiment))
    
conn.close()
