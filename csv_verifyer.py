from os import listdir
from os.path import isfile, join
import csv

"""
Verify CSV files for each tournament are in the same format
"""
directory = "./tourney_csvs/"

standard_headers = []
headers_correct = True
different_headers = []
first_file = ""

# Get all names of CSVs
files = [f for f in listdir(directory) if isfile(join(directory, f))]
for f in files:
    if first_file == "":
        first_file = f

    #Open file
    with open(directory + f, 'rb') as csvfile:
        rows = list(csv.reader(csvfile))

        #compare headers to that of the first file processed
        if len(standard_headers) == 0:
            standard_headers = rows[0]
        else:
            for col in range(len(rows[0])):
                if standard_headers[col] != rows[0][col]:
                    headers_correct = False
                    different_headers.append(f)

if headers_correct:
    print("All csvs have the same column headers as " + f)
else:
    print("The following files have different headers than " + f)
    print(different_headers)
