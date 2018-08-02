import MySQLdb
import enum

class ratings(enum.Enum):
    A = 6
    B = 5
    C = 4
    D = 3
    E = 2
    U = 1

try:
    db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
    cursor = db.cursor()
except:
    print("Error connecting.")


# Add new columns to instances
db.query("""ALTER TABLE instances ADD expected_placing VARCHAR(6)""")
db.query("""ALTER TABLE instances ADD placing_outcome INT""")

cursor = db.cursor()

# Get all tournament primary keys
cursor.execute("SELECT id FROM tournaments")
data = cursor.fetchall()

first = True
for t in data:
    # Get tournament result ids
    cursor.execute("SELECT id, rating_before FROM instances WHERE tournament_id ='" + t[0] + "'")
    tournament_results = cursor.fetchall()
    result_ids = []
    for result in tournament_results:
        rating = ""
        if result[1] != "":
            rating = result[1][0]
        result_ids.append([result[0], rating])

    # Get ratings in order
    cursor.execute("SELECT rating_before FROM instances WHERE tournament_id = '" + t[0] + "' ORDER BY rating_before")
    ordered_ratings = cursor.fetchall()
    sorted_ratings = []
    for rating in ordered_ratings:
        # Some tournaments have empty rating_before fields
        if rating[0] != "":
            sorted_ratings.append(rating[0][0])
    # Insert expected_placing and placing_outcome
    if len(sorted_ratings) > 0:
        for place in range(len(result_ids)):
            if result_ids[place][1] != "":
                actual = getattr(ratings, result_ids[place][1]).value
                expected = getattr(ratings, sorted_ratings[place]).value
                expected_placing = "expected_placing='" + sorted_ratings[place] + "'"
                # print(expected_placing)
                placing_outcome = "placing_outcome = '" + str(expected-actual) + "'"
                result_id = "'" + str(result_ids[place][0]) + "'"
                # print(result_id)
                cursor.execute("UPDATE instances SET " + expected_placing + "," + placing_outcome + "WHERE id=" + result_id)
    
cursor.close()
db.commit()
db.close()

    # if first = True:
    #     data = cursor.fetchall()


