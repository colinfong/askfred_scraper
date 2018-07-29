from os import listdir
from os.path import isfile, join
import csv
import MySQLdb

def MMDDYYYY_to_YYYYMMDD(date):
    formatted = ""
    formatted += date[6:len(date)]
    formatted += '-'
    formatted += date[0:2]
    formatted += '-'
    formatted += date[3:5]
    return formatted

db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
# print(type(db))

#rebuilding the table everytime for reproducible sharing, temporary
db.query("""DROP TABLE IF EXISTS tournaments;""")
db.query("""DROP TABLE IF EXISTS instances;""")

# Can revisit the length of varchars for appropriateness?
db.query(""" 
CREATE TABLE tournaments (
                            id INT NOT NULL AUTO_INCREMENT,
                            date DATE,
                            tournament VARCHAR(50),
                            event VARCHAR(50),
                            weapon VARCHAR(10),
                            event_gender VARCHAR(10),
                            rating_restriction VARCHAR(15),
                            age_restriction VARCHAR(15),
                            event_rating VARCHAR(15),
                            event_size INT,
                            PRIMARY KEY (id)
)
""")
db.query("""
CREATE TABLE instances (
                            id INT,
                            place INT,
                            last_name VARCHAR(30),
                            first_name VARCHAR(30),
                            club VARCHAR(30),
                            usfa_num INT,
                            rating_before VARCHAR(6),
                            rating_earned VARCHAR(6),
                            tournament_id INT,
                            PRIMARY KEY (id)
)
""")

directory = "./tourney_csvs/"
standard_headers = []
headers_correct = True
different_headers = []
first_file = ""

# Get all names of CSVs
files = [f for f in listdir(directory) if isfile(join(directory, f))]
f = "3783.csv"

if first_file == "":
    first_file = f

#Open file
with open(directory + f, 'r') as csvfile:
    rows = list(csv.reader(csvfile))

# Col 0:9 for tournaments table
# Col 9:len(rows[0]) for instances table
#print(rows[1][9:len(rows[0])])
#print(rows[1][0:9])

rows[1][0] = MMDDYYYY_to_YYYYMMDD(rows[1][0])
row = rows[1][:9] #temp to avoid formatting date and deal only with string

#to do: check for uniqueness of row before appending to tournaments, loop through one csv, loop through all csvs

cursor = db.cursor()
query_string = 'INSERT INTO tournaments (date, tournament, event, weapon, event_gender, rating_restriction, age_restriction, event_rating, event_size) \
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'
cursor.execute(query_string, row)

cursor.execute("SELECT * FROM tournaments;")
print(cursor.fetchone())