import requests
from bs4 import BeautifulSoup

#test_url = "https://askfred.net/Results/results.php?tournament_id=39072"
#test_url = "https://askfred.net/Results/results.php?tournament_id=10071"


def get_csv_link(tournament_url):
    print("Getting CSV from:", tournament_url)
    page = requests.get(tournament_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # get side bar with all links including csv download
    results_head = list(soup.find_all('div', id='other-links')[0])
    index_of_csv_div = find_csv_index(results_head)
    a_tag = list(results_head[index_of_csv_div].children)[0]
    href = a_tag.get('href')
    print("Success!")
    return href

def find_csv_index(head):
    csv_link_start = "https://askfred.net/Committee/Downloads/tourResultsCSV"
    for index in range(0, len(head)):
        try:
            a_tag = list(head[index].children)[0]
            href = a_tag.get('href')
            # 54 for index up to /tourResultsCSV
            if href[:54] == csv_link_start:
                return index
        except:
            #this is probably a bad way to handle errors/the new lines. advice?
            continue
    return -1

#print(get_csv_link(test_url))