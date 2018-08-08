from os import listdir
from os.path import isfile, join
import csv
import MySQLdb
from datetime import datetime

tournament_id = 0
result_id = 1

def is_new_tournament(old_tournament, new_tournament):
    if len(old_tournament) != len(new_tournament):
        return True
    for index in range(0, len(old_tournament)):
        if old_tournament[index] != new_tournament[index]:
            return True
    return False

def single_csv_to_db(f):
    #Open file
    with open(directory + f, 'r', encoding = "ISO-8859-1") as csvfile:
        rows = list(csv.reader(csvfile))

    date_index = 0
    split_index = 9
    usfa_index = 13
    event_size_index = 8

    tournament_row_prev = []

    # Brings tournament_id into scope
    global tournament_id
    global result_id

    for row_index in range(1, len(rows)):
        # Format Date and NULL for empty USFA numbers and empty events
        rows[row_index][date_index] = datetime.strptime(rows[row_index][date_index], '%m/%d/%Y').strftime('%Y-%m-%d')

        if rows[row_index][usfa_index] == '':
            rows[row_index][usfa_index] = None
        
        if rows[row_index][event_size_index] == '':
            rows[row_index][event_size_index] = None

        # Prepare for comparison
        tournament_row = rows[row_index][:split_index]

        # Handles tournament changes in CSV (Creates new row in tournaments)
        if is_new_tournament(tournament_row_prev, tournament_row):
            tournament_row_prev = tournament_row.copy()
            tournament_id += 1
            tournament_row.insert(0, str(tournament_id))
            

            query_string = 'INSERT INTO tournaments (id, date, tournament, event, weapon, event_gender, rating_restriction, age_restriction, event_rating, event_size) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
            cursor.execute(query_string, tournament_row)
        else:
            tournament_row_prev = tournament_row.copy()

        # Creates new row in tournament_result
        tournament_result_row = rows[row_index][split_index:len(rows[1])]
        tournament_result_row.insert(0, str(tournament_id))
        tournament_result_row.insert(0, str(result_id))
        result_id += 1
        #print(tournament_result_row)

        query_string = 'INSERT INTO tournament_results (id, tournament_id, place, last_name, first_name, club, usfa_num, rating_before, rating_earned) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'
        cursor.execute(query_string, tournament_result_row)



# Program to populate the database 'fencing'

try:
    db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
    cursor = db.cursor()
except:
    print("Error connecting.")


#rebuilding the table everytime for reproducible sharing, temporary
db.query("""DROP TABLE IF EXISTS tournament_results;""")
db.query("""DROP TABLE IF EXISTS tournaments;""")


# Can revisit the length of varchars for appropriateness?
db.query(""" 
CREATE TABLE tournaments (
                            id INT NOT NULL,
                            date DATE,
                            tournament VARCHAR(200),
                            event VARCHAR(300),
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
CREATE TABLE tournament_results (
                            id INT NOT NULL,
                            tournament_id INT NOT NULL,
                            place INT,
                            last_name VARCHAR(200),
                            first_name VARCHAR(200),
                            club VARCHAR(75),
                            usfa_num INT,
                            rating_before VARCHAR(6),
                            rating_earned VARCHAR(6),
                            PRIMARY KEY (id)
)
""")



directory = "../tourney_csvs/"

# Get all names of CSVs
files = [f for f in listdir(directory) if isfile(join(directory, f))]

# Populate the database
for file in files:
    single_csv_to_db(file)


db.query("""
ALTER TABLE tournament_results
ADD CONSTRAINT fk_tournament_id
FOREIGN KEY (tournament_id)
REFERENCES tournaments(id)
""")

# cursor.execute("SELECT * FROM tournaments LIMIT 100;")

# while True:
#     table_row = cursor.fetchone()
#     if table_row == None:
#         break
#     print(table_row)

# cursor.execute("SELECT * FROM tournament_results LIMIT 100;")

# while True:
#     table_row = cursor.fetchone()
#     if table_row == None:
#         break
#     print(table_row)

cursor.close()
db.commit()
db.close()
