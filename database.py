from os import listdir
from os.path import isfile, join
import csv
import MySQLdb
import uuid

def MMDDYYYY_to_YYYYMMDD(date):
    formatted = ""
    formatted += date[6:len(date)]
    formatted += '-'
    formatted += date[0:2]
    formatted += '-'
    formatted += date[3:5]
    return formatted

def is_new_tournament(old_tournament, new_tournament):
    print("Old Length: " + str(len(old_tournament)))
    print("New Length: " + str(len(new_tournament)))
    if len(old_tournament) != len(new_tournament):
        return True
    for index in range(0, len(old_tournament)):
        print(index)
        if old_tournament[index] != new_tournament[index]:
            return True
    return False

db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
cursor = db.cursor()

#rebuilding the table everytime for reproducible sharing, temporary
db.query("""DROP TABLE IF EXISTS tournaments;""")
db.query("""DROP TABLE IF EXISTS instances;""")

# Can revisit the length of varchars for appropriateness?
db.query(""" 
CREATE TABLE tournaments (
                            id CHAR(36) NOT NULL,
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
                            id INT NOT NULL AUTO_INCREMENT,
                            tournament_id CHAR(36) NOT NULL,
                            place INT,
                            last_name VARCHAR(30),
                            first_name VARCHAR(30),
                            club VARCHAR(75),
                            usfa_num INT,
                            rating_before VARCHAR(6),
                            rating_earned VARCHAR(6),
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

date_index = 0
split_index = 9
usfa_index = 13

tournament_row_prev = []
tournament_uuid = ""

for row_index in range(1, len(rows)):
    # Format Date and NULL for empty USFA numbers
    rows[row_index][date_index] = MMDDYYYY_to_YYYYMMDD(rows[row_index][date_index])

    if rows[row_index][usfa_index] == '':
        rows[row_index][usfa_index] = None

    # Prepare for comparison
    tournament_row = rows[row_index][:split_index]

    # Handles tournament changes in CSV (New UUID, creates new row in tournaments)
    if is_new_tournament(tournament_row_prev, tournament_row):
        tournament_row_prev = tournament_row.copy()
        tournament_uuid = uuid.uuid4()
        tournament_row.insert(0, tournament_uuid)

        query_string = 'INSERT INTO tournaments (id, date, tournament, event, weapon, event_gender, rating_restriction, age_restriction, event_rating, event_size) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        cursor.execute(query_string, tournament_row)
    else:
        tournament_row_prev = tournament_row.copy()

    # Creates new row in instance
    #instance_uuid = uuid.uuid4()
    instance_row = rows[row_index][split_index:len(rows[1])]
    instance_row.insert(0, tournament_uuid)
    #instance_row.insert(0, instance_uuid)

    query_string = 'INSERT INTO instances (tournament_id, place, last_name, first_name, club, usfa_num, rating_before, rating_earned) \
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
    cursor.execute(query_string, instance_row)

cursor.execute("SELECT * FROM tournaments;")

while True:
    table_row = cursor.fetchone()
    if table_row == None:
        break
    print(table_row)

cursor.execute("SELECT * FROM instances;")

while True:
    table_row = cursor.fetchone()
    if table_row == None:
        break
    print(table_row)

cursor.close()
db.commit()
db.close()
