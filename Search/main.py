"""googlesearch is a Python library for searching Google, easily."""
from time import sleep
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import unquote # to decode the url
from Search.useragentka import get_useragent
from curl_cffi import requests as curlreq
from Search.gettyimages import get_images

def _req(term, results, lang, start, proxies, timeout, safe, ssl_verify, region):
    resp = get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": get_useragent(),
            "Accept": "*/*"
        },
        params={
            "q": term,
            "num": results + 2,  # Prevents multiple requests
            "hl": lang,
            "start": start,
            "safe": safe,
            "gl": region,
        },
        proxies=proxies,
        timeout=timeout,
        verify=ssl_verify,
        cookies = {
            'CONSENT': 'PENDING+987', # Bypasses the consent page
            'SOCS': 'CAESHAgBEhIaAB',
        }
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5, safe="active", ssl_verify=None, region=None, start_num=0, unique=False):
    """Search the Google search engine"""

    # Proxy setup
    proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http")) else None

    start = start_num
    fetched_results = 0
    fetched_links = set()
    results_list = []
    image_results = []  # New list for image results

    while fetched_results < num_results:
        # Send request
        resp = _req(term, num_results - start,
                    lang, start, proxies, timeout, safe, ssl_verify, region)
        
        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", class_="ezO2md")
        new_results = 0

        # Find all images on the page
        try:
            all_images = soup.find_all("img", class_="rg_i")  # Google's image class
            for img in all_images:
                img_src = img.get("src") or img.get("data-src")
                if img_src and img_src.startswith("http"):
                    image_results.append({
                        "src": img_src,
                        "alt": img.get("alt", ""),
                        "class": img.get("class", [])
                    })
        except Exception as e:
            print(f"Error parsing images: {str(e)}")

        for result in result_block:
            link_tag = result.find("a", href=True)
            title_tag = link_tag.find("span", class_="CVA68e") if link_tag else None
            description_tag = result.find("span", class_="FrIlee")

            if link_tag and title_tag and description_tag:
                link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", ""))
                if link in fetched_links and unique:
                    continue
                fetched_links.add(link)
                title = title_tag.text if title_tag else ""
                description = description_tag.text if description_tag else ""

                # Only get page_text if advanced mode and we haven't gotten any yet
                if advanced and not any('page_text' in result for result in results_list):
                    try:
                        page_scrape = curlreq.get(link, impersonate='chrome110')
                        page_scrape.encoding = 'utf-8'
                        page_soup = BeautifulSoup(page_scrape.text, "html.parser")
                        
                        # Try multiple strategies to find main content
                        main_content = (
                            page_soup.find(['article', 'main']) or
                            page_soup.find('div', {'id': ['content', 'main-content', 'body-content']}) or
                            page_soup.find('div', {'class': ['content', 'main', 'article', 'post']}) or
                            page_soup.find('div', {'role': 'main'}) or
                            page_soup.body
                        )
                        if main_content:
                            # Remove unwanted elements
                            for element in main_content(['script', 'style', 'noscript', 'svg', 'header', 'footer', 'nav']):
                                element.decompose()
                            # Extract text with better cleaning
                            text = main_content.get_text(separator=' ', strip=True)
                            text = ' '.join(line.strip() for line in text.splitlines() if line.strip())
                            page_text = ' '.join(word for word in text.split() if len(word) > 1)[:3000]
                        else:
                            page_text = ""
                    except Exception as e:
                        print(f"Error scraping {link}: {str(e)}")
                        page_text = ""
                else:
                    page_text = ""


                fetched_results += 1
                new_results += 1
                
                if advanced:
                    results_list.append({
                        "link": link,
                        "title": title,
                        "description": description,
                        "page_text": page_text,
                    })
                else:
                    results_list.append(link)

                if fetched_results >= num_results:
                    break

        if new_results == 0:
            break

        start += 10
        sleep(sleep_interval)

    if image_results == [] :
        images = get_images(term)
        return {"results": results_list, "images": images}
    else:
        return {"results": results_list, "images": image_results}
