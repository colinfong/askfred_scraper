import MySQLdb
import enum
import math

success = 0
fail = 0

# 11557 successes 228 failures as of August 13, 2018


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
        self.result_ids_and_ratings = self._retrieve_result_ids()
        self.sorted_ratings = self._calculate_sorted_ratings()
        self.rating_counts = self._calculate_rating_counts()

        cursor.close()
        db.commit()
        db.close()

    # number of participants is number of rows pulled for a particular tournament id
    def _calculate_number_of_participants(self):
        cursor.execute("SELECT * FROM tournament_results WHERE tournament_id = " + str(self.id_num) + ";")
        number_of_participants = len(cursor.fetchall())
        # print("Participants: " + str(number_of_participants) + ".")
        return number_of_participants

    def _retrieve_result_ids(self):
        # Get all results of a single tournament
        cursor.execute("SELECT id, rating_before FROM tournament_results WHERE tournament_id =" + str(self.id_num) + "")
        tournament_results = cursor.fetchall()
        result_ids_and_ratings = []
        for result in tournament_results:
            rating = ""
            if result[1] != "":
                # First character of rating EX: A2012
                rating = result[1][0]
            # Result ID and rating before of ID
            result_ids_and_ratings.append([result[0], rating])
        return result_ids_and_ratings
    
    def _calculate_sorted_ratings(self):
        # Get ratings in order
        cursor.execute("SELECT rating_before FROM tournament_results WHERE tournament_id = " + str(self.id_num) + " ORDER BY rating_before")
        ordered_ratings = cursor.fetchall()
        sorted_ratings = []
        for rating in ordered_ratings:
            # Some tournaments have empty rating_before fields
            if rating[0] != "":
                sorted_ratings.append(rating[0][0])
        return sorted_ratings
    
    def _calculate_rating_counts(self):
        rating_counts = [['A', 0], ['B', 0], ['C', 0], ['D', 0], ['E', 0], ['U', 0]]
        rating_count_index = 0
        sorted_rating_index = 0
        # count through ratings
        while sorted_rating_index < len(self.sorted_ratings):
            rating = self.sorted_ratings[sorted_rating_index]
            count = 0
            # finds next rating from rating_counts
            while rating_counts[rating_count_index][0] != rating:
                rating_count_index += 1
            # while the ratings are equal, keep going through the sorted list
            while rating == rating_counts[rating_count_index][0]:
                count += 1
                sorted_rating_index += 1
                if sorted_rating_index > len(self.sorted_ratings) - 1:
                    break
                rating = self.sorted_ratings[sorted_rating_index][0]
            # add the final count to the current rating
            rating_counts[rating_count_index][1] = count
            #print(rating_counts)
        #print("Number of Participants (check against counts): " + self.number_of_participants)
        return rating_counts

# class to build a single row, helps organize methods
class Stats_Row(Tournament):
    def __init__(self, tournament, tournament_results_id, tournament_id, place, last_name, first_name, rating_before):

        self.tournament = tournament
        self.tournament_results_id = tournament_results_id
        self.tournament_id = tournament_id
        self.place = place
        self.last_name = last_name
        self.first_name = first_name
        if rating_before != "":
            # print("rating before: " + rating_before) 1st problem at 420
            self.rating_before = rating_before[0]
        else:
            self.rating_before = "U"

        # calculations
        try: 
            self.inverted_placement = self._calculate_inverted_placement()
            self.expected_rating_for_placement = self._calculate_expected_rating_for_placement()
            self.weighted_performance = self._calculate_weighted_performance()
            self.performance_points = self._calculate_performance_points()
            # median expected placement?
            self.expected_placement = self._calculate_expected_placement()
            self.expected_performance_points = self._calculate_expected_performance_points()
        except:
            print("Error calculating.")
            raise

    # builds a query to insert row
    def get_insert_query(self):
        # long debugging query
        # query = "first_name: " + self.first_name + " expected_rating_for_placement: " + self.expected_rating_for_placement + " weighted_performance: " + str(self.weighted_performance) + " inverted_placement: " + str(self.inverted_placement) + " performance_points: " + str(self.performance_points) + " expected_placement: " + str(self.expected_placement) + " expected_performance_points: " + str(self.expected_performance_points) + " performance points: " + str(self.performance_points)
        query = "INSERT INTO performance_statistics (tournament_results_id, tournament_id, last_name, first_name, inverted_placement, expected_rating_for_placement, weighted_performance, performance_points, expected_placement, expected_performance_points) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        return query

    # following methods used to performance row calculations during __init__
    # can't be used without db cursor

    def _calculate_inverted_placement(self):

        #cursor.execute("SELECT place FROM tournament_results WHERE id = " + str(self.tournament_results_id) + ";")
        #placement = cursor.fetchall()[0][0]
        # print("Placement: " + str(placement))
        return self.tournament.number_of_participants - self.place + 1

    def _calculate_performance_points(self):
        return self.weighted_performance * self.inverted_placement

    def _calculate_expected_performance_points(self):
        # expected_weighted_performance == 1 for current model (placing within bracket)
        return 1 * self.expected_placement

    def _calculate_expected_placement(self):
        rating_index = 0
        count_index = 1
        expected_placement = 0

        for index in range(len(self.tournament.rating_counts)):
            
            iterate_rating = self.tournament.rating_counts[index][rating_index]
            iterate_count = self.tournament.rating_counts[index][count_index]

            # add on counts above the person
            if iterate_rating != self.rating_before:
                expected_placement += iterate_count
            # add half the number of placements in fencer's rating bracket
            if iterate_rating == self.rating_before:
                if (iterate_count % 2 == 0):
                    expected_placement += iterate_count/2
                else:
                    expected_placement += math.ceil(iterate_count/2)
                break

        # print("rating: " + self.rating_before)
        # print("expected: " + str(expected_placement))
        return expected_placement

    def _calculate_weighted_performance(self):
        if self.tournament.number_of_participants > 0:
            if self.tournament.result_ids_and_ratings[self.place - 1][1] != "":
                actual = getattr(ratings, self.tournament.result_ids_and_ratings[self.place - 1][1]).value
                expected = getattr(ratings, self.tournament.sorted_ratings[self.place - 1]).value
        # 1 to remove push up 0 weights (what about -1 weights? does that make sense)
        return expected - actual + 1

    def _calculate_expected_rating_for_placement(self):
        # Insert expected_rating_for_placement and weighted_performance
        if self.tournament.number_of_participants > 0:
            if self.tournament.result_ids_and_ratings[self.place - 1][1] != "":
                expected_rating_for_placement = self.tournament.sorted_ratings[self.place - 1]
                return expected_rating_for_placement



# adds 'n' rows to the stats table given a tournament ID (where n = number of participants in tournament)
def add_tournament_stats(tournament_id, db_cursor):

    print("Loading tournament number: " + str(tournament_id))

    # grabs essential information from tournament results to duplicate in stats table
    db_cursor.execute("SELECT id, tournament_id, place, last_name, first_name, rating_before FROM tournament_results WHERE \
    tournament_id = " + str(tournament_id) + ";")
    tournament_results = db_cursor.fetchall()

    this_tournament = Tournament(tournament_id)

    global success
    global fail
    # builds and inserts a stats row corresponding to each entry in tournament results
    for row in tournament_results:

        tournament_results_id = row[0]
        tournament_id = row[1]
        place = row[2]
        last_name = row[3]
        first_name = row[4]
        rating_before = row[5]
        # print(row)

        try:
            current_row = Stats_Row(this_tournament, tournament_results_id, tournament_id, place, last_name, first_name, rating_before)
        except:
            print("Failed to build row where tournament_results(id) = " + str(tournament_results_id))
        
        try:
            db_cursor.execute(current_row.get_insert_query(), (tournament_results_id, tournament_id, last_name, first_name, current_row.inverted_placement, current_row.expected_rating_for_placement, current_row.weighted_performance, current_row.performance_points, current_row.expected_placement, current_row.expected_performance_points))
            success += 1
        except:
            print("Failed to load row where tournament_results(id) = " + str(tournament_results_id))
            fail += 1








########### Program to add table ###########

try:
    db=MySQLdb.connect(db="fencing",user="root",read_default_file="~/.my.cnf")
    cursor = db.cursor()
except:
    print("Error connecting.")

# Temporary to test building database
db.query("""DROP TABLE IF EXISTS performance_statistics;""")

db.query("""CREATE TABLE performance_statistics (
                                                id INT NOT NULL AUTO_INCREMENT,
                                                tournament_results_id INT NOT NULL,
                                                tournament_id INT NOT NULL,
                                                last_name VARCHAR(200),
                                                first_name VARCHAR(200),
                                                inverted_placement INT,
                                                expected_rating_for_placement VARCHAR(6),
                                                weighted_performance INT,
                                                performance_points INT,
                                                expected_placement INT,
                                                expected_performance_points INT,
                                                PRIMARY KEY (id)
)""")

cursor.execute("SELECT id FROM tournaments;")
tournament_ids = cursor.fetchall()
id_index = 0

for row in tournament_ids:
    id_num = row[id_index]
    add_tournament_stats(id_num, cursor)

print("Done loading rows with " + str(success) + " successes and" + str(fail) + " failures.")

# can't yet add foreign key constraint due to loading failures

# db.query("""
# ALTER TABLE performance_statistics
# ADD CONSTRAINT fk_tournament_results_id
# FOREIGN KEY (tournament_results_id)
# REFERENCES tournaments_results(id)
# """)

cursor.close()
db.commit()
db.close()
