import requests
import re

# Enter the url to the division search page to paginate all tournament IDs
def get_all_ids(div):
    can_paginate = True
    all_ids = []
    page_id = 1
    
    # Read all pages until page with no info reached
    while can_paginate:
        page_str = ""
        if page_id > 1:
            page_str = "&page_id=" + str(page_id)
        page = requests.get(div + page_str)

        #print(page.status_code)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(page.content, 'html.parser')

        # Retrieve the next sibling of the 'Email The Organizers' button
        # That anchor tag may be greyed out
        # Greyed out links are insufficient tournaments
        email_org = list(soup.find_all('a', title = "Email The Organizers"))
        tourney_ids = []
        for e in email_org:
            next = e.next_sibling.next_sibling
            # print(next)
            # print(next['href'])
            # Real tournaments have a real link
            if next['href'] != "#":
                matches = re.findall(".*_id=([0-9]*)", next['href'])
                tourney_ids.append(matches[0])
        print("Checking page " + str(page_id))
        print("Length of tourney_ids = "  + str(len(tourney_ids)))
        if len(tourney_ids) != 0:
            all_ids.extend(tourney_ids)
            page_id += 1
        else:
            can_paginate = False
    return all_ids



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
print(all_ids)