import json
from scraping_tournament_csv_link import get_csv_link
from search_scraper import get_all_ids
import os
import errno

#Foil/All Gender/Senior/is before 7-11-2018
#Northern California
n_cal = "https://askfred.net/Results/past.php?f%5Bevent_weapon_eq%5D=Foil&f%5Bevent_gender_eq%5D=&f%5Bevent_age_eq%5D=senior&f%5Bradius_mi%5D=300&vals%5Bloc%5D=&f%5Bname_contains%5D=&ops%5Bdate%5D=start_date_lte&vals%5Bdate%5D=07%2F11%2F2018&f%5Bevent_is_team%5D=&f%5Bevent_entries_gte%5D=&ops%5Bevent_rating%5D=event_rating_eq&vals%5Bevent_rating%5D=&f%5Bdivision_ids%5D%5B%5D=6"
#Central California
c_cal = "https://askfred.net/Results/past.php?f%5Bevent_weapon_eq%5D=Foil&f%5Bevent_gender_eq%5D=&f%5Bevent_age_eq%5D=senior&f%5Bradius_mi%5D=300&vals%5Bloc%5D=&f%5Bname_contains%5D=&ops%5Bdate%5D=start_date_lte&vals%5Bdate%5D=07%2F11%2F2018&f%5Bevent_is_team%5D=&f%5Bevent_entries_gte%5D=&ops%5Bevent_rating%5D=event_rating_eq&vals%5Bevent_rating%5D=&f%5Bdivision_ids%5D%5B%5D=3"
#Mountain Valley
m_valley = "https://askfred.net/Results/past.php?f%5Bevent_weapon_eq%5D=Foil&f%5Bevent_gender_eq%5D=&f%5Bevent_age_eq%5D=senior&f%5Bradius_mi%5D=300&vals%5Bloc%5D=&f%5Bname_contains%5D=&ops%5Bdate%5D=start_date_lte&vals%5Bdate%5D=07%2F11%2F2018&f%5Bevent_is_team%5D=&f%5Bevent_entries_gte%5D=&ops%5Bevent_rating%5D=event_rating_eq&vals%5Bevent_rating%5D=&f%5Bdivision_ids%5D%5B%5D=4"

all_ids = []
all_ids.extend(get_all_ids(n_cal))
all_ids.extend(get_all_ids(c_cal))
all_ids.extend(get_all_ids(m_valley))

all_ids = [id.encode("utf-8") for id in all_ids]
# print(all_ids)

# Grabs all the CSV links given all the IDs as a list
def get_all_csv_links(tourney_ids):

    tournament_url = make_tournament_urls(tourney_ids)
    csv_links = []

    failure = 0
    success = 0

    for url in tournament_url:
        try:
            csv_url = get_csv_link(url)
            print(csv_url)
            csv_links.append(csv_url)
            success += 1
        except:
            print("could not get csv url")
            failure += 1

    print("URLs retrieved with", success, "successes and", failure, "failures.")
    return csv_links

# Appends tournament IDs onto the URL
def make_tournament_urls(tourney_ids):
    csv_url_format = "https://askfred.net/Results/results.php?tournament_id="
    tourney_urls = []
    for tourney_id in tourney_ids:
        tourney_urls.append(csv_url_format + tourney_id.decode("utf-8"))
    return tourney_urls

    
# Grabs all the links and stores them in a JSON file
all_csv = get_all_csv_links(all_ids)

filename = "./output/all_csv_links.json"
if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

with open(filename, 'w') as outfile:
    json.dump(all_csv, outfile)