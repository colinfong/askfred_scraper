import requests
import json
import os
import errno
import re

with open("./output/all_csv_links.json") as f:
    data = json.load(f)

for i,csv_link in enumerate(data):
    matches = re.findall(".*_id=([0-9]*)", csv_link)
    tournament_id = matches[0]
    print("Downloading " + str(tournament_id) + " from " + csv_link)
    print(str(i+1) + " of " + str(len(data)))
    filename = "./tourney_csvs/" + str(tournament_id) + ".csv"
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    
    r = requests.get(csv_link, allow_redirects=True)
    with open(filename, "w") as f:
        f.write(r.content)