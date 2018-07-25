import requests
from bs4 import BeautifulSoup

page = requests.get("https://askfred.net/Results/results.php?tournament_id=39072")
soup = BeautifulSoup(page.content, 'html.parser')

results_head = list(soup.find_all('div', id='other-links')[0])
index_of_csv_div = 9
a_tag = list(results_head[7].children)[0]
href = a_tag.get('href')

print(href)