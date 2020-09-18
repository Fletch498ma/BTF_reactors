"""
Script that generates average pollutant concentration for each metric that we are collecting in the 
range hood experments.  It is important that the experiments table be filled out with the proper
cooking start and end times so that averages can be taken over this interval.  For each table
queried, a csv file is generated that can be imported into Excel or IGOR.

Edit to see how merge works.
Edit again to see how merges work.
"""
import psycopg2
import numpy as np

#These are the experiments to grab data from
Experiments = range(1,25,1)

#Make a database connection.  This connection is made over the internet.
conn = psycopg2.connect("host='mmlunden-s67.dhcp.lbl.gov' port='5432' dbname='mydb' user='melissa' password='postgres'")
cur = conn.cursor()

#These are the tables that will be queried against the experiment table.  The first entry is the
#table name, followed by the field that holds the timestamp information for that table followed 
#by the metrics that you would like to see averaged over the cooking period.
TableDefs = [
		["metone", "metonetime", ["metone03", "metone05", "metone07", "metone1", "metone2", "metone5"]],
		["api", "apitime", ["no", "no2", "nox"]],
		["dusttrak", "dusttraktime", ["dtconc"]],
		["teclog", "teclogtime", ["bd", "db", "egm"]],
        ["ucpc", "cpctime", ["cn"]]
	]

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
		
def ReturnQuery(Table, TimeField, Fields):
	"""
	Builds the query string and returns the string back to the calling function.  The arguments that it takes are:

	Table - the name of the table that will be queried against the experiments table
	TimeField - The field in the Table that holds the timestamp data.
	Fields - These are the metrics that need to be averaged.
	"""
	Query = "SELECT e.experiment,"
	
	Count = 0
	for Field in Fields:
		Query += " (SELECT avg({}) FROM {} m WHERE m.{} >= e.starttime AND m.{} < e.endtime)".format(Field,Table,TimeField,TimeField)
		if Count < len(Fields) - 1:
			Query += ','
		else:
			Query += " FROM experiments e ORDER BY e.experiment"
			
			return Query
		Count += 1
def AppendToMasterTable(AllExperiments, GasResults):
    ExperimentRowCount = 0
    for ExperimentRow in AllExperiments:
        GasRowCount = 0
        for GasRow in GasResults:
            if GasRow[0] == ExperimentRow[0]:
                ColCount = 1
                while ColCount < len(GasRow):
                    AllExperiments[ExperimentRowCount] += GasRow[ColCount],
                    ColCount += 1
                
                break
            GasRowCount += 1
        ExperimentRowCount += 1
    return AllExperiments
    
def HTMLSummary():
    """
    Output summary tables in HTML format.  This will be convenient for review purposes.  Make one big
    flat file?  That would be easiest to import into Excel for everybody else.
    
    First generate a table of experiments.  Grab summary results for each instrument and append to the
    experiment table making sure to align the experiment number.
    """
    Output = open('Results.html', 'w')
    Output.write( "<html><head><title>Summary</title></head>\n")
    Query = "SELECT * FROM experiments ORDER BY experiment"
    
    cur.execute(Query)
    AllExperiments = cur.fetchall()
    
    for Table, TimeField, Fields in TableDefs:
        print(Table)
        Query = ReturnQuery(Table, TimeField, Fields)
        cur.execute(Query)
        
        GasResults = cur.fetchall()
        AppendToMasterTable(AllExperiments, GasResults)

    cur.execute("SELECT MAX(experiment) FROM experiments")
    MaxExperiment = cur.fetchone()
    AppendToMasterTable(AllExperiments,GetGasVolume(range(1,int(MaxExperiment[0])+1,1)))
    
    Output.write("<table border=\"1\">\n")
    #Need to generate table headers here
    Query = "select column_name from information_schema.columns where table_name='experiments';"
    cur.execute(Query)
    Rows = cur.fetchall()
    
    Output.write("\t<tr>\n")
    for Row in Rows:
        Output.write("\t\t<th>{}</th>\n".format(Row[0]))
        
    for  Table, TimeField, Fields in TableDefs:
        for Field in Fields:
            Output.write("\t\t<th>{}</th>\n".format(Field))
    Output.write("\t\t<th>Gas Volume</th>\n\t</tr>\n")
    
    #Write out all data
    for ExperimentRow in AllExperiments:
        Output.write( "\t<tr>\n")
        for ExpVal in ExperimentRow:
            Output.write( "\t\t<td>{}</td>\n".format(ExpVal))
        Output.write("\t</tr>\n")
    Output.write( "</table>")
    Output.write( "</body>\n</html>")
HTMLSummary()

"""
GasResults = GetGasVolume(Experiments)
GasOut = open("gas", 'w')
GasOut.write("Experiment,GasConsumed(L)\n")

for GasResult in GasResults:
	print "{},{}".format(GasResult[0], GasResult[1])
	GasOut.write( "{},{}\n".format(GasResult[0], GasResult[1]))

GasOut.close()
	

for Table, TimeField, Fields in TableDefs:
	print Table
	Query = ReturnQuery(Table, TimeField, Fields)
	
	Output = open(Table, 'w')
	Output.write("Experiment," + ','.join(Fields) + "\n")
	
	cur.execute(Query)
	
	Rows = cur.fetchall()
	
	for Row in Rows:
		Count = 0
		
		while Count < len(Row):
			
			if Count < len(Row) - 1:
				Output.write("{},".format(Row[Count]))
			else:
				Output.write("{}\n".format(Row[Count]))
			
			Count += 1
	
	Output.close()
"""
