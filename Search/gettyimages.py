from curl_cffi import requests
from bs4 import BeautifulSoup

def get_images(query):
    res = requests.get(f'https://www.gettyimages.in/search/2/image?phrase={query}=editorial', impersonate='chrome110')

    soup = BeautifulSoup(res.text, 'html.parser')
    
    images = soup.find_all('img')
    
    results = []

    for image in images:
        print(image['src'])
        if image['src'].startswith('https://media.gettyimages.com'):
            results.append({'src': image['src'], 'alt': image['alt'], 'class':''})
        else:
            continue

    return results

