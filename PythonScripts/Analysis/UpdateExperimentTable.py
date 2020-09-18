import psycopg2
import os
import time

Types = [
    'Wok 2',
    'Fry Pan 1',
    'Oven'
    ]
    
Hoods = [
    "NO HOOD",
    'Vent-A-Hood'
    ]

HoodStates = [
    'ON',
    'OFF'
    ]

Foods = [
    "Trader Joe's Tarte Aux Champignons",
    "Trader Joe's Chunky Chocolate Chip Cookie Dough",
    "Trader Joe's Traditional Latkes: Potato Pancakes",
    "Trader Joe's Snow Peas (255 g)",
    "Trader Joe's Asparagus, Trimmed (340 g)",
    "Trader Joe's Pizza Parlanno with Italian sausage, uncured pepperoni, roasted peppers and roasted onions",
    "Pot of water",
    "Trader Joe's Organic Green Beans (454 g)",
    "Mazola Corn Oil",
    "DiGiorno Rising Crust Pepperoni PIzza"
    ]
    
conn = psycopg2.connect(database='mydb', user='melissa', password='postgres')
cur = conn.cursor()


#Get the next experiment number in the queue
Select = "select max(experiment) from experiments"
cur.execute(Select)
Experiment = cur.fetchone()[0] + 1
os.system('cls')
print "Next experiment in queue: {}".format(Experiment)

#Get all the rest of the information necessary for this experiment.
def GetUserInput(Types):
    Count = 1
    
    for Type in Types:
        print "{}.: {}".format(Count, Type)
        Count += 1
        
    UserChoice = raw_input("Enter your choice: ")
    Type = Types[int(UserChoice) - 1]
    return Type

print "\n\nSelect which type of cooking"
Type = GetUserInput(Types)

os.system('cls')
print "Select the food that was cooked"
Food = GetUserInput(Foods)

os.system('cls')
print "Select the hood used"
Hood = GetUserInput(Hoods)

os.system('cls')
print "Select the hood state"
HoodState = GetUserInput(HoodStates)

os.system('cls')
UserChoice = raw_input( "Experiment take place today? [y/n]")
if 'y' in UserChoice:
    DateString = time.strftime("%Y-%m-%d ")

    StartTime = raw_input('Enter time when cooking STARTED (hh:mm:ss): ')
    StartTime = DateString + StartTime
    EndTime = raw_input('Enter time when cooking STOPPED (hh:mm:ss): ')
    EndTime = DateString + EndTime
else:
    StartTime = raw_input('Enter time when cooking STARTED (mm/dd/yyyy hh:mm:ss): ')
    EndTime = raw_input('Enter time when cooking STOPPED (mm/dd/yyyy hh:mm:ss): ')

#Update the database
Insert = "insert into experiments (experiment,type,starttime,endtime,hood,hoodstate, food) values (%s,%s,%s,%s,%s,%s,%s)"
cur.execute(Insert, (Experiment, Type, StartTime, EndTime, Hood, HoodState, Food))
conn.commit()

conn.close()