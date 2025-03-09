from curl_cffi import requests
from bs4 import BeautifulSoup

res = requests.get('https://www.gettyimages.in/search/2/image?phrase=upsc%20exam&family=editorial', impersonate='chrome110')

soup = BeautifulSoup(res.text, 'html.parser')

images = soup.find_all('img')

results = [{'src': image['src'], 'alt': image['alt']} for image in images]

print(results)
