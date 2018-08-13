import MySQLdb
import enum

# values associated with each rating
class ratings(enum.Enum):
    A = 6
    B = 5
    C = 4
    D = 3
    E = 2
    U = 1


# class to store tournament calculations that only need to happen once
class Tournament:
    def __init__(self, id_num):
        self.id_num = id_num

        try:
            db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
            cursor = db.cursor()
        except:
            print("Error connecting.")

        self.number_of_participants = self._calculate_number_of_participants()
        self.ratings = self._retrieve_ratings()

        cursor.close()
        db.commit()
        db.close()

    # number of participants is number of rows pulled for a particular tournament id
    def _calculate_number_of_participants(self):
        cursor.execute("SELECT * FROM tournament_results WHERE tournament_id = " + str(self.id_num) + ";")
        number_of_participants = len(cursor.fetchall())
        # print("Participants: " + str(number_of_participants) + ".")
        return number_of_participants

    def _retrieve_ratings(self):
        # Get all results of a single tournament
        cursor.execute("SELECT id, rating_before FROM tournament_results WHERE tournament_id =" + str(self.id_num) + "")
        tournament_results = cursor.fetchall()
        result_ids = []
        for result in tournament_results:
            rating = ""
            if result[1] != "":
                # First character of rating EX: A2012
                rating = result[1][0]
            # Result ID and rating before of ID
            result_ids.append([result[0], rating])
        return result_ids

# class to build a single row, helps organize methods
class Stats_Row(Tournament):
    def __init__(self, tournament, tournament_results_id, tournament_id, last_name, first_name):

        self.tournament = tournament
        self.tournament_results_id = tournament_results_id
        self.tournament_id = tournament_id
        self.last_name = last_name
        self.first_name = first_name

        # database connection for handling calculations
        try:
            db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
            cursor = db.cursor()
        except:
            print("Error connecting.")
            raise

        # calculations
        try: 
            self.inverted_placement = self._calculate_inverted_placement()
            #self.expected_rating_for_placement = self._calculate_expected_rating_for_placement()
            #self.weighted_performance = self._calculate_weighted_performance()
            #self.performance_points = self._calculate_performance_points()
            #self.expected_placement = self._calculate_expected_placement()
            #self.expected_performance_points = self._calculate_expected_performance_points()
        except:
            print("Error calculating.")
            raise

        cursor.close()
        db.commit()
        db.close()

    # builds a query to insert row
    def get_insert_query(self):
        query = "inverted_placement: " + str(self.inverted_placement)
        return query

    # following methods used to performance row calculations during __init__
    # can't be used without db cursor

    def _calculate_inverted_placement(self):

        cursor.execute("SELECT place FROM tournament_results WHERE id = " + str(self.tournament_results_id) + ";")
        placement = cursor.fetchall()[0][0]
        # print("Placement: " + str(placement))
        return self.tournament.number_of_participants - placement + 1

    def _calculate_performance_points(self):
        return None

    def _calculate_expected_performance_points(self):
        return None

    def _calculate_expected_placement(self):
        return None

    def _calculate_weighted_performance(self):
        return None

    def _calculate_expected_rating_for_placement(self):
        '''
        # Get ratings in order
        cursor.execute("SELECT rating_before FROM tournament_results WHERE tournament_id = " + str(self.tournament_id) + " ORDER BY rating_before")
        ordered_ratings = cursor.fetchall()
        sorted_ratings = []
        for rating in ordered_ratings:
            # Some tournaments have empty rating_before fields
            if rating[0] != "":
                sorted_ratings.append(rating[0][0])
        # Insert expected_rating_for_placement and weighted_performance
        if len(sorted_ratings) > 0:
            for place in range(len(result_ids)):
                if result_ids[place][1] != "":
                    actual = getattr(ratings, result_ids[place][1]).value
                    expected = getattr(ratings, sorted_ratings[place]).value
                    expected_rating_for_placement = "expected_rating_for_placement='" + sorted_ratings[place] + "'"
                    # print(expected_rating_for_placement)
                    weighted_performance = "weighted_performance = '" + str(expected-actual) + "'"
                    result_id = "'" + str(result_ids[place][0]) + "'"
                    # print(result_id)
                    cursor.execute("UPDATE tournament_results SET " + expected_rating_for_placement + "," + weighted_performance + "WHERE id=" + result_id)
        '''
        return None







# adds 'n' rows to the stats table given a tournament ID (where n = number of participants in tournament)
def add_tournament_stats(tournament_id, db_cursor):

    # grabs essential information from tournament results to duplicate in stats table
    db_cursor.execute("SELECT id, tournament_id, place, last_name, first_name FROM tournament_results WHERE \
    tournament_id = " + str(tournament_id) + ";")
    tournament_results = db_cursor.fetchall()

    this_tournament = Tournament(tournament_id)
    print(this_tournament.ratings)

    print("\n NEW TOURNAMENT \n")
    # builds and inserts a stats row corresponding to each entry in tournament results
    for row in tournament_results:

        tournament_results_id = row[0]
        tournament_id = row[1]
        last_name = row[3]
        first_name = row[4]
        # print(row)

        try:
            current_row = Stats_Row(this_tournament, tournament_results_id, tournament_id, last_name, first_name)
            print(current_row.get_insert_query())
        except:
            print("Failed to build row where tournament_results(id) = " + str(tournament_results_id))






########### Program to add table ###########

try:
    db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
    cursor = db.cursor()
except:
    print("Error connecting.")

# Temporary to test building database
db.query("""DROP TABLE IF EXISTS performance_statistics;""")

db.query("""CREATE TABLE performance_statistics (
                                                id INT NOT NULL,
                                                tournament_results_id INT NOT NULL,
                                                tournament_id INT NOT NULL,
                                                last_name VARCHAR(200),
                                                first_name VARCHAR(200),
                                                inverted_placement INT,
                                                expected_rating_for_placement VARCHAR(6),
                                                weighted_performance INT,
                                                performance_points INT,
                                                expected_placement INT,
                                                expected_performance_points INT
)""")

cursor.execute("SELECT id FROM tournaments LIMIT 2")
tournament_ids = cursor.fetchall()
id_index = 0

for row in tournament_ids:
    id_num = row[id_index]
    add_tournament_stats(id_num, cursor)

# db.query("""
# ALTER TABLE performance_statistics
# ADD CONSTRAINT fk_tournament_id
# FOREIGN KEY (tournament_id)
# REFERENCES tournaments(id)
# """)

# db.query("""
# ALTER TABLE performance_statistics
# ADD CONSTRAINT fk_tournament_results_id
# FOREIGN KEY (tournament_results_id)
# REFERENCES tournaments_results(id)
# """)

cursor.close()
db.commit()
db.close()
