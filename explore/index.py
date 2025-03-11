from curl_cffi import requests
from bs4 import BeautifulSoup

def get_trending_news():
    url = 'https://www.ndtv.com/trends'
    response = requests.get(url, impersonate='chrome110')
    text = response.text
    soup = BeautifulSoup(text, 'html.parser')
    news = soup.find_all('div', class_='TrnLstPg_txt-wrp')
    news_headline = [item.find('a').text.strip() for item in news]
    return news_headline